import json
import logging
from langchain_core.messages import HumanMessage, SystemMessage
from app.agent.state import AgentState
from app.agent.prompts import CHART_GENERATOR_PROMPT

logger = logging.getLogger(__name__)

DEFAULT_COLORS = [
    "#6366f1", "#8b5cf6", "#a78bfa", "#c4b5fd",
    "#818cf8", "#4f46e5", "#4338ca", "#3730a3",
    "#ec4899", "#f43f5e",
]


def chart_generator_node(state: AgentState, llm) -> dict:
    """Generate a structured chart configuration from query results."""
    user_query = state["user_query"]
    results_json = state["query_results"]
    chart_config = state.get("chart_config", {})
    chart_type = chart_config.get("chart_type", "bar") if chart_config else "bar"

    try:
        results_list = json.loads(results_json)
    except json.JSONDecodeError:
        results_list = []

    if not results_list:
        return {"chart_config": None}

    columns = list(results_list[0].keys())
    display_rows = results_list[:30]

    prompt = CHART_GENERATOR_PROMPT.format(
        chart_type=chart_type,
        user_query=user_query,
        columns=", ".join(columns),
        results=json.dumps(display_rows, indent=2, default=str),
    )

    response = llm.invoke([
        SystemMessage(content="You are a data visualization configuration expert. Output only valid JSON."),
        HumanMessage(content=prompt),
    ])

    raw = response.content.strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        config = json.loads(raw)
        config.setdefault("colors", DEFAULT_COLORS)
        config.setdefault("chart_type", chart_type)

        logger.info("Chart config generated: %s with %d data points",
                     config.get("chart_type"), len(config.get("data", [])))
        return {
            "chart_config": config,
            "status_updates": [
                {"step": "chart_generated", "message": "Chart visualization ready"}
            ],
        }
    except json.JSONDecodeError as e:
        logger.error("Failed to parse chart config JSON: %s", e)
        return {
            "chart_config": None,
            "needs_chart": False,
            "status_updates": [
                {"step": "chart_error", "message": "Could not generate chart"}
            ],
        }
