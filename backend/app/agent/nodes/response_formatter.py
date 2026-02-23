import logging
from langchain_core.messages import AIMessage
from app.agent.state import AgentState

logger = logging.getLogger(__name__)


def response_formatter_node(state: AgentState) -> dict:
    """Combine analysis text and chart config into the final response."""
    analysis = state.get("analysis", "")
    chart_config = state.get("chart_config")
    sql_query = state.get("generated_sql", "")

    if not analysis:
        analysis = "I was unable to generate an analysis for your question. Please try rephrasing."

    return {
        "messages": [AIMessage(content=analysis)],
        "status_updates": [
            {"step": "complete", "message": "Response ready"}
        ],
    }
