import json
import logging
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage

from app.models.schemas import ChatRequest
from app.agent.graph import build_graph
from app.db.database import db_manager

logger = logging.getLogger(__name__)
router = APIRouter()

_graph = None
_sessions: dict[str, list] = {}


def _get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


def _sse_event(event_type: str, data: dict) -> str:
    return f"event: {event_type}\ndata: {json.dumps(data, default=str)}\n\n"


def _invoke_graph(message: str, session_id: str) -> dict:
    """Run the agent synchronously and return final state."""
    graph = _get_graph()
    history = _sessions.get(session_id, [])
    history.append(HumanMessage(content=message))

    initial_state = {
        "messages": history,
        "user_query": message,
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

    return graph.invoke(initial_state)


async def _stream_response(message: str, session_id: str):
    """Run the LangGraph agent and stream SSE events."""
    if not db_manager.is_loaded:
        yield _sse_event("error", {"message": "Database not loaded. Check server logs."})
        yield _sse_event("done", {})
        return

    try:
        yield _sse_event("status", {"step": "starting", "message": "Processing your question..."})
        await asyncio.sleep(0)

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _invoke_graph, message, session_id)

        statuses = []
        query_type = result.get("query_type", "unknown")
        statuses.append({"step": "routing", "message": f"Query classified as: {query_type}"})

        if query_type == "data_analysis":
            if result.get("relevant_columns"):
                statuses.append({"step": "schema", "message": "Identified relevant columns"})
            if result.get("generated_sql"):
                statuses.append({"step": "sql_generated", "message": "SQL query generated"})
            if result.get("query_results"):
                statuses.append({"step": "executed", "message": "Query executed successfully"})
            if result.get("analysis"):
                statuses.append({"step": "analyzed", "message": "Analysis complete"})
            if result.get("needs_chart"):
                statuses.append({"step": "chart", "message": "Chart visualization generated"})

        for status in statuses:
            yield _sse_event("status", status)
            await asyncio.sleep(0.03)

        if result.get("generated_sql"):
            yield _sse_event("sql", {"query": result["generated_sql"]})
            await asyncio.sleep(0)

        analysis = result.get("analysis", "")
        if result.get("messages"):
            last_msg = result["messages"][-1]
            if hasattr(last_msg, "content") and last_msg.content:
                analysis = last_msg.content

        if not analysis:
            error = result.get("error", "")
            if error:
                analysis = f"I encountered an error: {error}\n\nPlease try rephrasing your question."
            else:
                analysis = "I wasn't able to process your question. Please try rephrasing it."

        chunk_size = 15
        for i in range(0, len(analysis), chunk_size):
            chunk = analysis[i:i + chunk_size]
            yield _sse_event("token", {"content": chunk})
            await asyncio.sleep(0.01)

        chart_config = result.get("chart_config")
        if chart_config and isinstance(chart_config, dict) and chart_config.get("data"):
            yield _sse_event("chart", chart_config)

        if result.get("messages"):
            _sessions[session_id] = result["messages"][-20:]

        yield _sse_event("done", {})

    except Exception as e:
        logger.exception("Error in agent execution")
        yield _sse_event("error", {"message": str(e)})
        yield _sse_event("done", {})


@router.post("/chat")
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    return StreamingResponse(
        _stream_response(request.message, request.session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
