from fastapi import APIRouter

from src.schemas.cooking import CookingModeResponse, ScaleRecipeRequest
from src.services.cooking_service import get_cooking_mode_flow, scale_recipe_flow

router = APIRouter(prefix="/cooking", tags=["cooking"])


# PUBLIC_INTERFACE
@router.get(
    "/recipes/{recipe_id}",
    response_model=CookingModeResponse,
    summary="Get cooking mode payload",
    description="Return cooking-mode friendly recipe data with steps, timers, and scaled ingredients.",
    operation_id="getCookingMode",
)
async def get_cooking_mode(recipe_id: str, target_servings: int | None = None) -> CookingModeResponse:
    """Return the cooking mode view of a recipe."""
    return await get_cooking_mode_flow(recipe_id, target_servings)


# PUBLIC_INTERFACE
@router.post(
    "/scale",
    response_model=CookingModeResponse,
    summary="Scale a recipe",
    description="Scale a recipe to a requested number of servings and return cooking-mode friendly data.",
    operation_id="scaleRecipe",
)
async def scale_recipe(request: ScaleRecipeRequest) -> CookingModeResponse:
    """Scale a recipe by servings."""
    return await scale_recipe_flow(request)
