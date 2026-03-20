from __future__ import annotations

import re
from typing import Any

from fastapi import HTTPException, status

from src.core.database import fetch_all, fetch_one
from src.core.logging import get_logger
from src.schemas.cooking import CookingModeResponse, ScaleRecipeRequest, StepTimer

logger = get_logger("cooking_service")
_TIMER_PATTERN = re.compile(r"(\d+)\s*(minute|minutes|min)", re.IGNORECASE)


def _scale_quantity(quantity: str | None, factor: float) -> str | None:
    """Scale a simple numeric quantity string when possible."""
    if quantity is None:
        return None
    try:
        numeric = float(quantity)
        return str(round(numeric * factor, 2))
    except ValueError:
        return quantity


def _extract_timers(steps: list[dict[str, Any]]) -> list[StepTimer]:
    """Extract timers from step text and explicit duration columns."""
    timers: list[StepTimer] = []
    for step in steps:
        duration = step.get("duration_minutes")
        if duration:
            timers.append(
                StepTimer(
                    step_number=step["step_number"],
                    duration_minutes=int(duration),
                    label=f"Step {step['step_number']} timer",
                )
            )
            continue
        instruction = step.get("instruction") or ""
        match = _TIMER_PATTERN.search(instruction)
        if match:
            timers.append(
                StepTimer(
                    step_number=step["step_number"],
                    duration_minutes=int(match.group(1)),
                    label=f"Step {step['step_number']} timer",
                )
            )
    return timers


# PUBLIC_INTERFACE
async def get_cooking_mode_flow(recipe_id: str, target_servings: int | None = None) -> CookingModeResponse:
    """Return cooking-mode friendly recipe content including timers and scaled ingredients."""
    logger.info("get_cooking_mode_flow_start recipe_id=%s target_servings=%s", recipe_id, target_servings)
    recipe = await fetch_one(
        "SELECT id, title, servings FROM recipes WHERE id = $1",
        recipe_id,
    )
    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    ingredients = await fetch_all(
        """
        SELECT id, ingredient_name, quantity, unit, notes, position
        FROM recipe_ingredients
        WHERE recipe_id = $1
        ORDER BY position ASC, created_at ASC
        """,
        recipe_id,
    )
    steps = await fetch_all(
        """
        SELECT id, step_number, instruction, duration_minutes
        FROM recipe_steps
        WHERE recipe_id = $1
        ORDER BY step_number ASC
        """,
        recipe_id,
    )

    current_servings = recipe.get("servings")
    factor = 1.0
    if target_servings and current_servings and current_servings > 0:
        factor = target_servings / current_servings

    scaled_ingredients = []
    for ingredient in ingredients:
        scaled_ingredients.append(
            {
                **ingredient,
                "quantity": _scale_quantity(ingredient.get("quantity"), factor),
            }
        )

    return CookingModeResponse(
        recipe_id=str(recipe["id"]),
        title=recipe["title"],
        servings=target_servings or current_servings,
        scaled_ingredients=scaled_ingredients,
        steps=steps,
        timers=_extract_timers(steps),
    )


# PUBLIC_INTERFACE
async def scale_recipe_flow(request: ScaleRecipeRequest) -> CookingModeResponse:
    """Scale a recipe to a requested serving count."""
    return await get_cooking_mode_flow(request.recipe_id, request.target_servings)
