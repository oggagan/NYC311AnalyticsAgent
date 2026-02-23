import logging
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from app.agent.state import AgentState
from app.agent.prompts import GENERAL_RESPONSE_PROMPT

logger = logging.getLogger(__name__)


def general_response_node(state: AgentState, llm) -> dict:
    """Handle non-data-analysis queries (greetings, system info, etc.)."""
    user_query = state["user_query"]

    prompt = GENERAL_RESPONSE_PROMPT.format(user_query=user_query)

    response = llm.invoke([
        SystemMessage(content="You are a friendly analytics assistant."),
        HumanMessage(content=prompt),
    ])

    content = response.content.strip()
    logger.info("General response generated: %d chars", len(content))
    return {
        "messages": [AIMessage(content=content)],
        "analysis": content,
        "status_updates": [
            {"step": "complete", "message": "Response ready"}
        ],
    }
