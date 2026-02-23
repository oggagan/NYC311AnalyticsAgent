from pydantic import BaseModel, Field
from typing import Any


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(default="default")


class ChartConfig(BaseModel):
    chart_type: str = Field(..., description="bar, pie, line, or scatter")
    title: str
    data: list[dict[str, Any]]
    x_key: str
    y_key: str | list[str]
    x_label: str = ""
    y_label: str = ""
    colors: list[str] = Field(default_factory=lambda: [
        "#6366f1", "#8b5cf6", "#a78bfa", "#c4b5fd",
        "#818cf8", "#4f46e5", "#4338ca", "#3730a3",
        "#ec4899", "#f43f5e",
    ])


class ChatResponse(BaseModel):
    content: str
    chart: ChartConfig | None = None
    sql_query: str | None = None


class HealthResponse(BaseModel):
    status: str
    db_connected: bool
    rows_loaded: int
