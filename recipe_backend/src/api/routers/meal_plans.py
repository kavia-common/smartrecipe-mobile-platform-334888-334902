from datetime import date

from fastapi import APIRouter, status

from src.schemas.common import MessageResponse
from src.schemas.meal_plans import MealPlanItemCreateRequest, MealPlanItemResponse, MealPlanWeekResponse
from src.services.meal_plan_service import create_meal_plan_item_flow, delete_meal_plan_item_flow, get_meal_plan_week_flow

router = APIRouter(prefix="/meal-plans", tags=["meal-plans"])


# PUBLIC_INTERFACE
@router.get(
    "/{user_id}/week",
    response_model=MealPlanWeekResponse,
    summary="Get weekly meal plan",
    description="Return all meal plan items for a user's requested week.",
    operation_id="getMealPlanWeek",
)
async def get_meal_plan_week(user_id: str, week_start: date) -> MealPlanWeekResponse:
    """Return meal plan items for a one-week window."""
    return await get_meal_plan_week_flow(user_id, week_start)


# PUBLIC_INTERFACE
@router.post(
    "/items",
    response_model=MealPlanItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create meal plan item",
    description="Create a planned meal slot for a recipe on a specific date.",
    operation_id="createMealPlanItem",
)
async def create_meal_plan_item(request: MealPlanItemCreateRequest) -> MealPlanItemResponse:
    """Create a meal plan item."""
    return await create_meal_plan_item_flow(request)


# PUBLIC_INTERFACE
@router.delete(
    "/items/{item_id}",
    response_model=MessageResponse,
    summary="Delete meal plan item",
    description="Delete a meal plan item from the planner.",
    operation_id="deleteMealPlanItem",
)
async def delete_meal_plan_item(item_id: str) -> MessageResponse:
    """Delete a meal plan item."""
    await delete_meal_plan_item_flow(item_id)
    return MessageResponse(message="Meal plan item deleted")
