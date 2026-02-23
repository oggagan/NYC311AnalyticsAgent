import pytest
from app.agent.state import AgentState


def test_agent_state_structure():
    """Verify the AgentState has all required fields."""
    state: AgentState = {
        "messages": [],
        "user_query": "test query",
        "query_type": "",
        "relevant_columns": [],
        "generated_sql": "",
        "sql_valid": False,
        "query_results": "",
        "analysis": "",
        "needs_chart": False,
        "chart_config": None,
        "error": None,
        "retry_count": 0,
        "status_updates": [],
    }
    assert state["user_query"] == "test query"
    assert state["retry_count"] == 0
    assert state["chart_config"] is None


def test_agent_state_all_keys():
    expected_keys = {
        "messages", "user_query", "query_type", "relevant_columns",
        "generated_sql", "sql_valid", "query_results", "analysis",
        "needs_chart", "chart_config", "error", "retry_count", "status_updates",
    }
    assert set(AgentState.__annotations__.keys()) == expected_keys
