from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class MessageResponse(BaseModel):
    """Standard message response model."""

    message: str = Field(..., description="Human-readable response message.")


class HealthResponse(BaseModel):
    """Health endpoint response model."""

    status: str = Field(..., description="Service health status.")
    service: str = Field(..., description="Service name.")
    version: str = Field(..., description="Running API version.")


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    limit: int = Field(..., description="Maximum number of records returned.")
    offset: int = Field(..., description="Records skipped before this page.")
    total: int = Field(..., description="Total records matching the query.")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""

    items: list[T] = Field(..., description="Page items.")
    pagination: PaginationMeta = Field(..., description="Pagination metadata.")


class TimestampedResponse(BaseModel):
    """Base response carrying a generated timestamp."""

    generated_at: datetime = Field(..., description="Timestamp when the response was generated.")
