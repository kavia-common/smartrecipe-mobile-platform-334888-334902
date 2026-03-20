from __future__ import annotations

from fastapi import HTTPException, status

from src.core.database import execute, fetch_all, fetch_one
from src.core.logging import get_logger
from src.schemas.admin import AdminRecipeUpsertRequest, AdminTagRequest

logger = get_logger("admin_service")


async def _replace_recipe_children(recipe_id: str, request: AdminRecipeUpsertRequest) -> None:
    """Replace recipe child tables from the admin payload."""
    await execute("DELETE FROM recipe_ingredients WHERE recipe_id = $1", recipe_id)
    await execute("DELETE FROM recipe_steps WHERE recipe_id = $1", recipe_id)
    await execute("DELETE FROM recipe_images WHERE recipe_id = $1", recipe_id)
    await execute("DELETE FROM recipe_tags WHERE recipe_id = $1", recipe_id)

    for position, ingredient in enumerate(request.ingredients, start=1):
        await execute(
            """
            INSERT INTO recipe_ingredients (recipe_id, ingredient_name, quantity, unit, notes, position)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            recipe_id,
            ingredient.get("ingredient_name"),
            ingredient.get("quantity"),
            ingredient.get("unit"),
            ingredient.get("notes"),
            position,
        )
    for step in request.steps:
        await execute(
            """
            INSERT INTO recipe_steps (recipe_id, step_number, instruction, duration_minutes)
            VALUES ($1, $2, $3, $4)
            """,
            recipe_id,
            step.get("step_number"),
            step.get("instruction"),
            step.get("duration_minutes"),
        )
    for index, image_url in enumerate(request.image_urls, start=1):
        await execute(
            """
            INSERT INTO recipe_images (recipe_id, image_url, sort_order)
            VALUES ($1, $2, $3)
            """,
            recipe_id,
            image_url,
            index,
        )
    for tag_name in request.tags:
        tag = await fetch_one(
            """
            INSERT INTO tags (name)
            VALUES ($1)
            ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
            RETURNING id
            """,
            tag_name,
        )
        await execute(
            """
            INSERT INTO recipe_tags (recipe_id, tag_id)
            VALUES ($1, $2)
            ON CONFLICT DO NOTHING
            """,
            recipe_id,
            tag["id"],
        )


# PUBLIC_INTERFACE
async def upsert_recipe_flow(recipe_id: str | None, request: AdminRecipeUpsertRequest) -> dict[str, str]:
    """Create or update a recipe and fully replace its related records."""
    logger.info("upsert_recipe_flow_start recipe_id=%s title=%s", recipe_id, request.title)
    if recipe_id:
        updated = await fetch_one(
            """
            UPDATE recipes
            SET
                title = $2,
                description = $3,
                cuisine = $4,
                difficulty = $5,
                prep_time_minutes = $6,
                cook_time_minutes = $7,
                servings = $8,
                nutrition = $9,
                updated_at = NOW()
            WHERE id = $1
            RETURNING id
            """,
            recipe_id,
            request.title,
            request.description,
            request.cuisine,
            request.difficulty,
            request.prep_time_minutes,
            request.cook_time_minutes,
            request.servings,
            request.nutrition,
        )
        if updated is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
        target_recipe_id = str(updated["id"])
    else:
        created = await fetch_one(
            """
            INSERT INTO recipes (
                title,
                description,
                cuisine,
                difficulty,
                prep_time_minutes,
                cook_time_minutes,
                servings,
                nutrition
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
            """,
            request.title,
            request.description,
            request.cuisine,
            request.difficulty,
            request.prep_time_minutes,
            request.cook_time_minutes,
            request.servings,
            request.nutrition,
        )
        target_recipe_id = str(created["id"])

    await _replace_recipe_children(target_recipe_id, request)
    return {"id": target_recipe_id, "message": "Recipe saved successfully"}


# PUBLIC_INTERFACE
async def delete_recipe_flow(recipe_id: str) -> str:
    """Delete a recipe and dependent rows handled by the database."""
    logger.info("delete_recipe_flow_start recipe_id=%s", recipe_id)
    return await execute("DELETE FROM recipes WHERE id = $1", recipe_id)


# PUBLIC_INTERFACE
async def create_tag_flow(request: AdminTagRequest) -> dict[str, str]:
    """Create or upsert a taxonomy tag."""
    logger.info("create_tag_flow_start name=%s", request.name)
    tag = await fetch_one(
        """
        INSERT INTO tags (name, category)
        VALUES ($1, $2)
        ON CONFLICT (name) DO UPDATE SET category = EXCLUDED.category
        RETURNING id, name
        """,
        request.name,
        request.category,
    )
    return {"id": str(tag["id"]), "name": tag["name"]}


# PUBLIC_INTERFACE
async def list_tags_flow() -> list[dict[str, str | None]]:
    """List all tags for admin management."""
    rows = await fetch_all("SELECT id, name, category FROM tags ORDER BY name ASC")
    return [{"id": str(row["id"]), "name": row["name"], "category": row.get("category")} for row in rows]
