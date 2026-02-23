import json
import logging
from langchain_core.messages import HumanMessage, SystemMessage
from app.agent.state import AgentState
from app.agent.prompts import VIZ_DECIDER_PROMPT

logger = logging.getLogger(__name__)


def viz_decider_node(state: AgentState, llm) -> dict:
    """Decide whether a chart visualization should be generated."""
    user_query = state["user_query"]
    results_json = state["query_results"]

    try:
        results_list = json.loads(results_json)
    except json.JSONDecodeError:
        results_list = []

    if not results_list:
        return {
            "needs_chart": False,
            "status_updates": [
                {"step": "viz_decision", "message": "No visualization needed (no data)"}
            ],
        }

    columns = list(results_list[0].keys())
    row_count = len(results_list)

    prompt = VIZ_DECIDER_PROMPT.format(
        user_query=user_query,
        columns=", ".join(columns),
        row_count=row_count,
    )

    response = llm.invoke([
        SystemMessage(content="You are a data visualization expert."),
        HumanMessage(content=prompt),
    ])

    decision = response.content.strip().lower()
    needs_chart = decision != "no"
    chart_type = decision if needs_chart else None

    logger.info("Viz decision: %s", decision)
    return {
        "needs_chart": needs_chart,
        "chart_config": {"chart_type": chart_type} if chart_type else None,
        "status_updates": [
            {"step": "viz_decision", "message": f"Visualization: {decision}"}
        ],
    }
