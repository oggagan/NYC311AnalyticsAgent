import logging
import httpx
from functools import partial
from langgraph.graph import StateGraph, END
from langchain_deepseek import ChatDeepSeek

from app.agent.state import AgentState
from app.agent.nodes.router import router_node
from app.agent.nodes.schema_inspector import schema_inspector_node
from app.agent.nodes.query_generator import query_generator_node
from app.agent.nodes.query_validator import query_validator_node
from app.agent.nodes.query_executor import query_executor_node
from app.agent.nodes.analyzer import analyzer_node
from app.agent.nodes.viz_decider import viz_decider_node
from app.agent.nodes.chart_generator import chart_generator_node
from app.agent.nodes.response_formatter import response_formatter_node
from app.agent.nodes.general_response import general_response_node
from app.config import get_settings

logger = logging.getLogger(__name__)


def _route_after_router(state: AgentState) -> str:
    return "schema_inspector" if state["query_type"] == "data_analysis" else "general_response"


def _route_after_validator(state: AgentState) -> str:
    if state.get("sql_valid"):
        return "query_executor"
    if state.get("retry_count", 0) >= get_settings().max_retries:
        return "response_formatter"
    return "query_generator"


def _route_after_executor(state: AgentState) -> str:
    if state.get("error"):
        if state.get("retry_count", 0) >= get_settings().max_retries:
            return "response_formatter"
        return "query_generator"
    return "analyzer"


def _route_after_viz_decider(state: AgentState) -> str:
    return "chart_generator" if state.get("needs_chart") else "response_formatter"


def build_graph() -> StateGraph:
    """Build and compile the LangGraph agent."""
    settings = get_settings()
    http_client = httpx.Client(verify=False)
    llm = ChatDeepSeek(
        model=settings.llm_model,
        api_key=settings.deepseek_api_key,
        temperature=settings.llm_temperature,
        timeout=settings.llm_timeout,
        http_client=http_client,
    )

    graph = StateGraph(AgentState)

    graph.add_node("router", partial(router_node, llm=llm))
    graph.add_node("schema_inspector", partial(schema_inspector_node, llm=llm))
    graph.add_node("query_generator", partial(query_generator_node, llm=llm))
    graph.add_node("query_validator", partial(query_validator_node, llm=llm))
    graph.add_node("query_executor", query_executor_node)
    graph.add_node("analyzer", partial(analyzer_node, llm=llm))
    graph.add_node("viz_decider", partial(viz_decider_node, llm=llm))
    graph.add_node("chart_generator", partial(chart_generator_node, llm=llm))
    graph.add_node("response_formatter", response_formatter_node)
    graph.add_node("general_response", partial(general_response_node, llm=llm))

    graph.set_entry_point("router")

    graph.add_conditional_edges("router", _route_after_router)
    graph.add_edge("schema_inspector", "query_generator")
    graph.add_edge("query_generator", "query_validator")
    graph.add_conditional_edges("query_validator", _route_after_validator)
    graph.add_conditional_edges("query_executor", _route_after_executor)
    graph.add_edge("analyzer", "viz_decider")
    graph.add_conditional_edges("viz_decider", _route_after_viz_decider)
    graph.add_edge("chart_generator", "response_formatter")
    graph.add_edge("response_formatter", END)
    graph.add_edge("general_response", END)

    compiled = graph.compile()
    logger.info("LangGraph agent compiled successfully")
    return compiled
