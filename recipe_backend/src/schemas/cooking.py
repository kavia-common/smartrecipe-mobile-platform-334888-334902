from pydantic import BaseModel, Field


class ScaleRecipeRequest(BaseModel):
    """Request model for scaling a recipe by servings."""

    recipe_id: str = Field(..., description="Recipe identifier.")
    target_servings: int = Field(..., ge=1, description="Desired number of servings.")


class StepTimer(BaseModel):
    """Timer extracted from a recipe step."""

    step_number: int = Field(..., description="Step sequence number.")
    duration_minutes: int = Field(..., description="Timer duration in minutes.")
    label: str = Field(..., description="Timer label.")


class CookingModeResponse(BaseModel):
    """Response for cooking mode helper data."""

    recipe_id: str = Field(..., description="Recipe identifier.")
    title: str = Field(..., description="Recipe title.")
    servings: int | None = Field(default=None, description="Current serving count.")
    scaled_ingredients: list[dict] = Field(default_factory=list, description="Scaled ingredients.")
    steps: list[dict] = Field(default_factory=list, description="Step-by-step instructions.")
    timers: list[StepTimer] = Field(default_factory=list, description="Timers parsed from steps.")
