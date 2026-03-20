from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AnalyticsEventRequest(BaseModel):
    """Analytics event ingestion payload."""

    user_id: str | None = Field(default=None, description="Optional authenticated user identifier.")
    session_id: str | None = Field(default=None, description="Client session identifier.")
    event_name: str = Field(..., description="Analytics event name.")
    event_category: str | None = Field(default=None, description="Logical analytics category.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Structured event metadata.")
    occurred_at: datetime | None = Field(default=None, description="Client event timestamp.")


class AnalyticsEventResponse(BaseModel):
    """Stored analytics event response."""

    id: str = Field(..., description="Analytics event identifier.")
    accepted: bool = Field(..., description="Whether the event was accepted.")
