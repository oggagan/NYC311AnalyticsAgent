import json
import logging
from app.agent.state import AgentState
from app.db.database import db_manager

logger = logging.getLogger(__name__)

MAX_RESULT_ROWS = 500


def query_executor_node(state: AgentState) -> dict:
    """Execute the validated SQL against DuckDB."""
    sql = state["generated_sql"]
    logger.info("Executing SQL: %s", sql[:200])

    try:
        columns, rows = db_manager.execute_query(sql)

        if len(rows) > MAX_RESULT_ROWS:
            rows = rows[:MAX_RESULT_ROWS]

        result_dicts = [dict(zip(columns, row)) for row in rows]

        for d in result_dicts:
            for k, v in d.items():
                if hasattr(v, "isoformat"):
                    d[k] = v.isoformat()
                elif v is None:
                    d[k] = None
                else:
                    try:
                        json.dumps(v)
                    except (TypeError, ValueError):
                        d[k] = str(v)

        results_json = json.dumps(result_dicts, default=str)

        logger.info("Query returned %d rows, %d columns", len(rows), len(columns))
        return {
            "query_results": results_json,
            "error": None,
            "status_updates": [
                {"step": "query_executed", "message": f"Query returned {len(rows)} rows"}
            ],
        }

    except Exception as e:
        error_msg = str(e)
        logger.error("SQL execution failed: %s", error_msg)
        return {
            "query_results": "",
            "error": error_msg,
            "retry_count": state.get("retry_count", 0) + 1,
            "status_updates": [
                {"step": "execution_error", "message": f"Query error: {error_msg[:100]}"}
            ],
        }
