from datetime import date, timedelta

from src.core.database import execute, fetch_all, fetch_one
from src.core.logging import get_logger
from src.schemas.meal_plans import MealPlanItemCreateRequest, MealPlanItemResponse, MealPlanWeekResponse

logger = get_logger("meal_plan_service")


# PUBLIC_INTERFACE
async def create_meal_plan_item_flow(request: MealPlanItemCreateRequest) -> MealPlanItemResponse:
    """Create a meal plan item for a user."""
    logger.info(
        "create_meal_plan_item_flow_start user_id=%s recipe_id=%s planned_date=%s",
        request.user_id,
        request.recipe_id,
        request.planned_date,
    )
    row = await fetch_one(
        """
        INSERT INTO meal_plan_items (user_id, recipe_id, planned_date, meal_slot, servings)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id, user_id, recipe_id, planned_date, meal_slot, servings
        """,
        request.user_id,
        request.recipe_id,
        request.planned_date,
        request.meal_slot,
        request.servings,
    )
    recipe = await fetch_one("SELECT title FROM recipes WHERE id = $1", request.recipe_id)
    return MealPlanItemResponse(
        id=str(row["id"]),
        user_id=str(row["user_id"]),
        recipe_id=str(row["recipe_id"]),
        planned_date=row["planned_date"],
        meal_slot=row["meal_slot"],
        servings=row["servings"],
        recipe_title=recipe["title"] if recipe else None,
    )


# PUBLIC_INTERFACE
async def get_meal_plan_week_flow(user_id: str, week_start: date) -> MealPlanWeekResponse:
    """Return meal plan items for the requested week."""
    logger.info("get_meal_plan_week_flow_start user_id=%s week_start=%s", user_id, week_start)
    week_end = week_start + timedelta(days=6)
    rows = await fetch_all(
        """
        SELECT mpi.id, mpi.user_id, mpi.recipe_id, mpi.planned_date, mpi.meal_slot, mpi.servings, r.title AS recipe_title
        FROM meal_plan_items mpi
        JOIN recipes r ON r.id = mpi.recipe_id
        WHERE mpi.user_id = $1
          AND mpi.planned_date BETWEEN $2 AND $3
        ORDER BY mpi.planned_date ASC, mpi.meal_slot ASC
        """,
        user_id,
        week_start,
        week_end,
    )
    items = [
        MealPlanItemResponse(
            id=str(row["id"]),
            user_id=str(row["user_id"]),
            recipe_id=str(row["recipe_id"]),
            planned_date=row["planned_date"],
            meal_slot=row["meal_slot"],
            servings=row["servings"],
            recipe_title=row.get("recipe_title"),
        )
        for row in rows
    ]
    return MealPlanWeekResponse(week_start=week_start, week_end=week_end, items=items)


# PUBLIC_INTERFACE
async def delete_meal_plan_item_flow(item_id: str) -> str:
    """Delete a meal plan item."""
    logger.info("delete_meal_plan_item_flow_start item_id=%s", item_id)
    return await execute("DELETE FROM meal_plan_items WHERE id = $1", item_id)
