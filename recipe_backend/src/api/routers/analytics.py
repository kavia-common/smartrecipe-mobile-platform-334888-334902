from fastapi import APIRouter, status

from src.schemas.analytics import AnalyticsEventRequest, AnalyticsEventResponse
from src.services.analytics_service import ingest_analytics_event_flow

router = APIRouter(prefix="/analytics", tags=["analytics"])


# PUBLIC_INTERFACE
@router.post(
    "/events",
    response_model=AnalyticsEventResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Ingest analytics event",
    description="Store a client analytics event for downstream analysis.",
    operation_id="ingestAnalyticsEvent",
)
async def ingest_event(request: AnalyticsEventRequest) -> AnalyticsEventResponse:
    """Store an analytics event."""
    return await ingest_analytics_event_flow(request)
