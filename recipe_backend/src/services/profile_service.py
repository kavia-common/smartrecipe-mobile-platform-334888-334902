from fastapi import HTTPException, status

from src.core.database import execute, fetch_one
from src.core.logging import get_logger
from src.schemas.profile import DietaryPreferences, UpdateProfileRequest, UserProfileResponse

logger = get_logger("profile_service")


# PUBLIC_INTERFACE
async def get_profile_flow(user_id: str) -> UserProfileResponse:
    """Return a user's profile and dietary preferences."""
    logger.info("get_profile_flow_start user_id=%s", user_id)
    row = await fetch_one(
        """
        SELECT id, email, full_name, is_admin, diets, allergens, disliked_ingredients
        FROM users
        WHERE id = $1
        """,
        user_id,
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserProfileResponse(
        id=str(row["id"]),
        email=row["email"],
        full_name=row.get("full_name"),
        is_admin=bool(row.get("is_admin", False)),
        preferences=DietaryPreferences(
            diets=row.get("diets") or [],
            allergens=row.get("allergens") or [],
            disliked_ingredients=row.get("disliked_ingredients") or [],
        ),
    )


# PUBLIC_INTERFACE
async def update_profile_flow(user_id: str, request: UpdateProfileRequest) -> UserProfileResponse:
    """Update a user's profile and preference arrays."""
    logger.info("update_profile_flow_start user_id=%s", user_id)
    await execute(
        """
        UPDATE users
        SET
            full_name = COALESCE($2, full_name),
            diets = $3,
            allergens = $4,
            disliked_ingredients = $5,
            updated_at = NOW()
        WHERE id = $1
        """,
        user_id,
        request.full_name,
        request.diets,
        request.allergens,
        request.disliked_ingredients,
    )
    return await get_profile_flow(user_id)
