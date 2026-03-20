from datetime import date

from pydantic import BaseModel, Field


class MealPlanItemCreateRequest(BaseModel):
    """Create meal plan item request."""

    user_id: str = Field(..., description="User identifier.")
    recipe_id: str = Field(..., description="Recipe identifier.")
    planned_date: date = Field(..., description="Scheduled meal date.")
    meal_slot: str = Field(..., description="Meal slot such as breakfast, lunch, or dinner.")
    servings: int = Field(default=1, ge=1, description="Planned servings.")


class MealPlanItemResponse(BaseModel):
    """Meal plan item response."""

    id: str = Field(..., description="Meal plan item identifier.")
    user_id: str = Field(..., description="User identifier.")
    recipe_id: str = Field(..., description="Recipe identifier.")
    planned_date: date = Field(..., description="Scheduled meal date.")
    meal_slot: str = Field(..., description="Meal slot.")
    servings: int = Field(..., description="Planned servings.")
    recipe_title: str | None = Field(default=None, description="Associated recipe title.")


class MealPlanWeekResponse(BaseModel):
    """Weekly meal plan response."""

    week_start: date = Field(..., description="Inclusive week start date.")
    week_end: date = Field(..., description="Inclusive week end date.")
    items: list[MealPlanItemResponse] = Field(..., description="Meal plan items in the requested week.")
