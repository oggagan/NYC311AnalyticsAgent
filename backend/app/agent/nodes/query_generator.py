import logging
from langchain_core.messages import HumanMessage, SystemMessage
from app.agent.state import AgentState
from app.agent.prompts import QUERY_GENERATOR_PROMPT
from app.db.database import db_manager

logger = logging.getLogger(__name__)


def query_generator_node(state: AgentState, llm) -> dict:
    """Generate a DuckDB SQL query for the user's question."""
    user_query = state["user_query"]
    relevant_columns = state.get("relevant_columns", [])
    error = state.get("error")
    schema_info = db_manager.schema_info

    error_context = ""
    if error:
        error_context = (
            f"PREVIOUS ATTEMPT FAILED with error: {error}\n"
            f"Previous SQL: {state.get('generated_sql', '')}\n"
            "Fix the issue and generate a corrected query."
        )

    prompt = QUERY_GENERATOR_PROMPT.format(
        schema_info=schema_info,
        relevant_columns=", ".join(relevant_columns),
        user_query=user_query,
        error_context=error_context,
    )

    response = llm.invoke([
        SystemMessage(content="You are a DuckDB SQL expert."),
        HumanMessage(content=prompt),
    ])

    sql = response.content.strip()
    sql = sql.removeprefix("```sql").removeprefix("```").removesuffix("```").strip()

    logger.info("Generated SQL: %s", sql[:200])
    return {
        "generated_sql": sql,
        "sql_valid": False,
        "error": None,
        "status_updates": [
            {"step": "generating_sql", "message": "Generated SQL query"}
        ],
    }
