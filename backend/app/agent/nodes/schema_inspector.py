import logging
from langchain_core.messages import HumanMessage, SystemMessage
from app.agent.state import AgentState
from app.agent.prompts import SCHEMA_INSPECTOR_PROMPT
from app.db.database import db_manager

logger = logging.getLogger(__name__)


def schema_inspector_node(state: AgentState, llm) -> dict:
    """Identify relevant columns for the user's question."""
    user_query = state["user_query"]
    schema_info = db_manager.schema_info

    prompt = SCHEMA_INSPECTOR_PROMPT.format(
        schema_info=schema_info,
        user_query=user_query,
    )

    response = llm.invoke([
        SystemMessage(content="You are a data schema expert."),
        HumanMessage(content=prompt),
    ])

    columns = [
        line.strip().strip('"').strip("-").strip()
        for line in response.content.strip().split("\n")
        if line.strip() and not line.strip().startswith("#")
    ]

    logger.info("Relevant columns identified: %s", columns)
    return {
        "relevant_columns": columns,
        "status_updates": [
            {"step": "inspecting_schema", "message": "Identified relevant data columns"}
        ],
    }
