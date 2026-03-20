from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status

from src.core.database import execute, fetch_all, fetch_one
from src.core.logging import get_logger
from src.schemas.recipes import (
    CollectionCreateRequest,
    CollectionResponse,
    RecipeDetail,
    RecipeSearchResponse,
    RecipeSummary,
)
from src.services.utils import build_limit_offset

logger = get_logger("recipe_service")


def _map_recipe_summary(row: dict[str, Any]) -> RecipeSummary:
    """Convert a database row into a recipe summary model."""
    return RecipeSummary(
        id=str(row["id"]),
        title=row["title"],
        description=row.get("description"),
        cuisine=row.get("cuisine"),
        difficulty=row.get("difficulty"),
        prep_time_minutes=row.get("prep_time_minutes"),
        cook_time_minutes=row.get("cook_time_minutes"),
        image_url=row.get("image_url"),
    )


# PUBLIC_INTERFACE
async def search_recipes_flow(
    query: str | None,
    cuisine: str | None,
    difficulty: str | None,
    max_total_time: int | None,
    diets: list[str],
    allergens: list[str],
    ingredients: list[str],
    limit: int,
    offset: int,
) -> RecipeSearchResponse:
    """Search recipes using reusable filter construction."""
    logger.info(
        "search_recipes_flow_start query=%s cuisine=%s difficulty=%s",
        query,
        cuisine,
        difficulty,
    )
    limit, offset = build_limit_offset(limit, offset)

    clauses: list[str] = ["1=1"]
    args: list[Any] = []
    position = 1

    if query:
        clauses.append(f"(r.title ILIKE ${position} OR r.description ILIKE ${position})")
        args.append(f"%{query}%")
        position += 1
    if cuisine:
        clauses.append(f"r.cuisine = ${position}")
        args.append(cuisine)
        position += 1
    if difficulty:
        clauses.append(f"r.difficulty = ${position}")
        args.append(difficulty)
        position += 1
    if max_total_time is not None:
        clauses.append(f"(COALESCE(r.prep_time_minutes, 0) + COALESCE(r.cook_time_minutes, 0)) <= ${position}")
        args.append(max_total_time)
        position += 1
    if diets:
        clauses.append(f"NOT EXISTS (SELECT 1 FROM recipe_diet_exclusions de WHERE de.recipe_id = r.id AND de.diet = ANY(${position}::text[]))")
        args.append(diets)
        position += 1
    if allergens:
        clauses.append(f"NOT EXISTS (SELECT 1 FROM recipe_allergens ra WHERE ra.recipe_id = r.id AND ra.allergen = ANY(${position}::text[]))")
        args.append(allergens)
        position += 1
    if ingredients:
        clauses.append(
            f"EXISTS (SELECT 1 FROM recipe_ingredients ri WHERE ri.recipe_id = r.id AND ri.ingredient_name = ANY(${position}::text[]))"
        )
        args.append(ingredients)
        position += 1

    where_clause = " AND ".join(clauses)
    rows = await fetch_all(
        f"""
        SELECT
            r.id,
            r.title,
            r.description,
            r.cuisine,
            r.difficulty,
            r.prep_time_minutes,
            r.cook_time_minutes,
            (
                SELECT image_url
                FROM recipe_images img
                WHERE img.recipe_id = r.id
                ORDER BY img.sort_order NULLS LAST, img.created_at ASC
                LIMIT 1
            ) AS image_url
        FROM recipes r
        WHERE {where_clause}
        ORDER BY r.updated_at DESC NULLS LAST, r.created_at DESC NULLS LAST, r.title ASC
        LIMIT ${position}
        OFFSET ${position + 1}
        """,
        *args,
        limit,
        offset,
    )
    count_row = await fetch_one(
        f"SELECT COUNT(*) AS total FROM recipes r WHERE {where_clause}",
        *args,
    )
    return RecipeSearchResponse(
        items=[_map_recipe_summary(row) for row in rows],
        total=int(count_row["total"]) if count_row else 0,
    )


# PUBLIC_INTERFACE
async def get_recipe_detail_flow(recipe_id: str) -> RecipeDetail:
    """Return a detailed recipe aggregate by querying related tables."""
    logger.info("get_recipe_detail_flow_start recipe_id=%s", recipe_id)
    recipe = await fetch_one(
        """
        SELECT id, title, description, cuisine, difficulty, prep_time_minutes, cook_time_minutes, servings, nutrition
        FROM recipes
        WHERE id = $1
        """,
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
    tags = await fetch_all(
        """
        SELECT t.name
        FROM recipe_tags rt
        JOIN tags t ON t.id = rt.tag_id
        WHERE rt.recipe_id = $1
        ORDER BY t.name ASC
        """,
        recipe_id,
    )
    images = await fetch_all(
        """
        SELECT image_url
        FROM recipe_images
        WHERE recipe_id = $1
        ORDER BY sort_order NULLS LAST, created_at ASC
        """,
        recipe_id,
    )

    return RecipeDetail(
        id=str(recipe["id"]),
        title=recipe["title"],
        description=recipe.get("description"),
        cuisine=recipe.get("cuisine"),
        difficulty=recipe.get("difficulty"),
        prep_time_minutes=recipe.get("prep_time_minutes"),
        cook_time_minutes=recipe.get("cook_time_minutes"),
        servings=recipe.get("servings"),
        nutrition=recipe.get("nutrition") or {},
        ingredients=ingredients,
        steps=steps,
        tags=[tag["name"] for tag in tags],
        image_urls=[image["image_url"] for image in images],
    )


# PUBLIC_INTERFACE
async def add_favorite_flow(user_id: str, recipe_id: str) -> str:
    """Add a recipe to the user's favorites."""
    logger.info("add_favorite_flow_start user_id=%s recipe_id=%s", user_id, recipe_id)
    return await execute(
        """
        INSERT INTO user_favorites (user_id, recipe_id)
        VALUES ($1, $2)
        ON CONFLICT DO NOTHING
        """,
        user_id,
        recipe_id,
    )


# PUBLIC_INTERFACE
async def remove_favorite_flow(user_id: str, recipe_id: str) -> str:
    """Remove a recipe from the user's favorites."""
    logger.info("remove_favorite_flow_start user_id=%s recipe_id=%s", user_id, recipe_id)
    return await execute(
        "DELETE FROM user_favorites WHERE user_id = $1 AND recipe_id = $2",
        user_id,
        recipe_id,
    )


# PUBLIC_INTERFACE
async def list_favorites_flow(user_id: str) -> list[RecipeSummary]:
    """List favorite recipes for the specified user."""
    rows = await fetch_all(
        """
        SELECT
            r.id,
            r.title,
            r.description,
            r.cuisine,
            r.difficulty,
            r.prep_time_minutes,
            r.cook_time_minutes,
            (
                SELECT image_url
                FROM recipe_images img
                WHERE img.recipe_id = r.id
                ORDER BY img.sort_order NULLS LAST, img.created_at ASC
                LIMIT 1
            ) AS image_url
        FROM user_favorites uf
        JOIN recipes r ON r.id = uf.recipe_id
        WHERE uf.user_id = $1
        ORDER BY uf.created_at DESC
        """,
        user_id,
    )
    return [_map_recipe_summary(row) for row in rows]


# PUBLIC_INTERFACE
async def create_collection_flow(request: CollectionCreateRequest) -> CollectionResponse:
    """Create a user collection and return its summary."""
    logger.info("create_collection_flow_start user_id=%s", request.user_id)
    collection = await fetch_one(
        """
        INSERT INTO user_collections (user_id, name, description)
        VALUES ($1, $2, $3)
        RETURNING id, user_id, name, description
        """,
        request.user_id,
        request.name,
        request.description,
    )
    if collection is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Collection could not be created")
    return CollectionResponse(
        id=str(collection["id"]),
        user_id=str(collection["user_id"]),
        name=collection["name"],
        description=collection.get("description"),
        recipe_count=0,
    )


# PUBLIC_INTERFACE
async def list_collections_flow(user_id: str) -> list[CollectionResponse]:
    """Return user collections with recipe counts."""
    rows = await fetch_all(
        """
        SELECT
            c.id,
            c.user_id,
            c.name,
            c.description,
            COUNT(cr.recipe_id)::int AS recipe_count
        FROM user_collections c
        LEFT JOIN user_collection_recipes cr ON cr.collection_id = c.id
        WHERE c.user_id = $1
        GROUP BY c.id
        ORDER BY c.created_at DESC
        """,
        user_id,
    )
    return [
        CollectionResponse(
            id=str(row["id"]),
            user_id=str(row["user_id"]),
            name=row["name"],
            description=row.get("description"),
            recipe_count=row.get("recipe_count", 0),
        )
        for row in rows
    ]


# PUBLIC_INTERFACE
async def add_recipe_to_collection_flow(collection_id: str, recipe_id: str) -> str:
    """Add a recipe to a collection."""
    logger.info("add_recipe_to_collection_flow_start collection_id=%s recipe_id=%s", collection_id, recipe_id)
    return await execute(
        """
        INSERT INTO user_collection_recipes (collection_id, recipe_id)
        VALUES ($1, $2)
        ON CONFLICT DO NOTHING
        """,
        collection_id,
        recipe_id,
    )


# PUBLIC_INTERFACE
async def remove_recipe_from_collection_flow(collection_id: str, recipe_id: str) -> str:
    """Remove a recipe from a collection."""
    logger.info("remove_recipe_from_collection_flow_start collection_id=%s recipe_id=%s", collection_id, recipe_id)
    return await execute(
        "DELETE FROM user_collection_recipes WHERE collection_id = $1 AND recipe_id = $2",
        collection_id,
        recipe_id,
    )
