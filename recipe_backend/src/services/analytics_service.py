from datetime import UTC, datetime

from src.core.config import get_settings
from src.core.database import fetch_one
from src.core.logging import get_logger
from src.schemas.analytics import AnalyticsEventRequest, AnalyticsEventResponse

logger = get_logger("analytics_service")


# PUBLIC_INTERFACE
async def ingest_analytics_event_flow(request: AnalyticsEventRequest) -> AnalyticsEventResponse:
    """Persist an analytics event for later analysis."""
    logger.info("ingest_analytics_event_flow_start event_name=%s user_id=%s", request.event_name, request.user_id)
    settings = get_settings()
    row = await fetch_one(
        """
        INSERT INTO analytics_events (
            user_id,
            session_id,
            source,
            event_name,
            event_category,
            metadata,
            occurred_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING id
        """,
        request.user_id,
        request.session_id,
        settings.analytics_source,
        request.event_name,
        request.event_category,
        request.metadata,
        request.occurred_at or datetime.now(UTC),
    )
    return AnalyticsEventResponse(id=str(row["id"]), accepted=True)
