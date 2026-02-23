import logging
from langchain_core.messages import HumanMessage, SystemMessage
from app.agent.state import AgentState
from app.agent.prompts import QUERY_VALIDATOR_PROMPT
from app.db.database import db_manager

logger = logging.getLogger(__name__)


def query_validator_node(state: AgentState, llm) -> dict:
    """Validate the generated SQL query before execution."""
    sql_query = state["generated_sql"]
    user_query = state["user_query"]
    schema_info = db_manager.schema_info

    prompt = QUERY_VALIDATOR_PROMPT.format(
        schema_info=schema_info,
        sql_query=sql_query,
        user_query=user_query,
    )

    response = llm.invoke([
        SystemMessage(content="You are a SQL validator for DuckDB."),
        HumanMessage(content=prompt),
    ])

    result = response.content.strip()
    is_valid = result.upper().startswith("VALID")

    if not is_valid:
        error_msg = result.replace("INVALID:", "").strip()
        logger.warning("SQL validation failed: %s", error_msg)
        return {
            "sql_valid": False,
            "error": error_msg,
            "retry_count": state.get("retry_count", 0) + 1,
            "status_updates": [
                {"step": "validation_failed", "message": f"SQL needs correction: {error_msg[:100]}"}
            ],
        }

    logger.info("SQL validation passed")
    return {
        "sql_valid": True,
        "error": None,
        "status_updates": [
            {"step": "sql_validated", "message": "SQL query validated successfully"}
        ],
    }
