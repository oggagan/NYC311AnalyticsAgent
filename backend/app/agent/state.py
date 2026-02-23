from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    user_query: str
    query_type: str  # "data_analysis" | "general"
    relevant_columns: list[str]
    generated_sql: str
    sql_valid: bool
    query_results: str
    analysis: str
    needs_chart: bool
    chart_config: dict | None
    error: str | None
    retry_count: int
    status_updates: list[dict]
