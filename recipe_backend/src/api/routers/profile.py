from fastapi import APIRouter

from src.schemas.profile import UpdateProfileRequest, UserProfileResponse
from src.services.profile_service import get_profile_flow, update_profile_flow

router = APIRouter(prefix="/profile", tags=["profile"])


# PUBLIC_INTERFACE
@router.get(
    "/{user_id}",
    response_model=UserProfileResponse,
    summary="Get user profile",
    description="Return the specified user's profile and dietary preference settings.",
    operation_id="getUserProfile",
)
async def get_profile(user_id: str) -> UserProfileResponse:
    """Return a user's profile."""
    return await get_profile_flow(user_id)


# PUBLIC_INTERFACE
@router.put(
    "/{user_id}",
    response_model=UserProfileResponse,
    summary="Update user profile",
    description="Update a user's display name and dietary preference settings.",
    operation_id="updateUserProfile",
)
async def update_profile(user_id: str, request: UpdateProfileRequest) -> UserProfileResponse:
    """Update a user's profile and preferences."""
    return await update_profile_flow(user_id, request)
