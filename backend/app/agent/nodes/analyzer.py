import json
import logging
from langchain_core.messages import HumanMessage, SystemMessage
from app.agent.state import AgentState
from app.agent.prompts import ANALYZER_PROMPT

logger = logging.getLogger(__name__)


def analyzer_node(state: AgentState, llm) -> dict:
    """Analyze query results and generate insights."""
    user_query = state["user_query"]
    sql_query = state["generated_sql"]
    results_json = state["query_results"]

    try:
        results_list = json.loads(results_json)
    except json.JSONDecodeError:
        results_list = []

    if results_list:
        columns = list(results_list[0].keys())
        display_rows = results_list[:30]
        results_text = json.dumps(display_rows, indent=2, default=str)
    else:
        columns = []
        results_text = "No results returned."

    prompt = ANALYZER_PROMPT.format(
        user_query=user_query,
        sql_query=sql_query,
        columns=", ".join(columns),
        results=results_text,
    )

    response = llm.invoke([
        SystemMessage(content="You are a data analyst specializing in urban services data."),
        HumanMessage(content=prompt),
    ])

    analysis = response.content.strip()
    logger.info("Analysis generated: %d chars", len(analysis))
    return {
        "analysis": analysis,
        "status_updates": [
            {"step": "analysis_complete", "message": "Analysis generated"}
        ],
    }
