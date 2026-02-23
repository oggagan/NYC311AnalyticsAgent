import logging
from langchain_core.messages import HumanMessage, SystemMessage
from app.agent.state import AgentState
from app.agent.prompts import ROUTER_PROMPT

logger = logging.getLogger(__name__)


def router_node(state: AgentState, llm) -> dict:
    """Classify the user query as data_analysis or general."""
    user_query = state["user_query"]
    logger.info("Router classifying query: %s", user_query[:80])

    response = llm.invoke([
        SystemMessage(content=ROUTER_PROMPT),
        HumanMessage(content=user_query),
    ])

    query_type = response.content.strip().lower()
    if query_type not in ("data_analysis", "general"):
        query_type = "data_analysis"

    logger.info("Query classified as: %s", query_type)
    return {
        "query_type": query_type,
        "status_updates": [{"step": "routing", "message": f"Query type: {query_type}"}],
    }
