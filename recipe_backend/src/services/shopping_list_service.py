from src.core.database import execute, fetch_all, fetch_one
from src.core.logging import get_logger
from src.schemas.shopping_lists import (
    ShoppingListGenerateRequest,
    ShoppingListItemResponse,
    ShoppingListResponse,
)

logger = get_logger("shopping_list_service")


# PUBLIC_INTERFACE
async def generate_shopping_list_flow(request: ShoppingListGenerateRequest) -> ShoppingListResponse:
    """Generate a shopping list from meal plan items across a date range."""
    logger.info(
        "generate_shopping_list_flow_start user_id=%s start_date=%s end_date=%s",
        request.user_id,
        request.start_date,
        request.end_date,
    )
    shopping_list = await fetch_one(
        """
        INSERT INTO shopping_lists (user_id, start_date, end_date)
        VALUES ($1, $2, $3)
        RETURNING id, user_id, start_date, end_date
        """,
        request.user_id,
        request.start_date,
        request.end_date,
    )
    rows = await fetch_all(
        """
        SELECT
            ri.ingredient_name,
            COALESCE(string_agg(DISTINCT TRIM(CONCAT(ri.quantity, ' ', ri.unit)), ', '), '') AS quantity,
            COUNT(DISTINCT mpi.recipe_id)::int AS source_recipe_count
        FROM meal_plan_items mpi
        JOIN recipe_ingredients ri ON ri.recipe_id = mpi.recipe_id
        WHERE mpi.user_id = $1
          AND mpi.planned_date BETWEEN $2::date AND $3::date
        GROUP BY ri.ingredient_name
        ORDER BY ri.ingredient_name ASC
        """,
        request.user_id,
        request.start_date,
        request.end_date,
    )

    items: list[ShoppingListItemResponse] = []
    for row in rows:
        item = await fetch_one(
            """
            INSERT INTO shopping_list_items (shopping_list_id, ingredient_name, quantity, checked, source_recipe_count)
            VALUES ($1, $2, $3, FALSE, $4)
            RETURNING id, ingredient_name, quantity, checked, source_recipe_count
            """,
            shopping_list["id"],
            row["ingredient_name"],
            row["quantity"] or None,
            row["source_recipe_count"],
        )
        items.append(
            ShoppingListItemResponse(
                id=str(item["id"]),
                ingredient_name=item["ingredient_name"],
                quantity=item.get("quantity"),
                checked=item["checked"],
                source_recipe_count=item["source_recipe_count"],
            )
        )

    return ShoppingListResponse(
        id=str(shopping_list["id"]),
        user_id=str(shopping_list["user_id"]),
        start_date=str(shopping_list["start_date"]),
        end_date=str(shopping_list["end_date"]),
        items=items,
    )


# PUBLIC_INTERFACE
async def get_shopping_list_flow(shopping_list_id: str) -> ShoppingListResponse:
    """Fetch a shopping list and all of its items."""
    logger.info("get_shopping_list_flow_start shopping_list_id=%s", shopping_list_id)
    shopping_list = await fetch_one(
        "SELECT id, user_id, start_date, end_date FROM shopping_lists WHERE id = $1",
        shopping_list_id,
    )
    items = await fetch_all(
        """
        SELECT id, ingredient_name, quantity, checked, source_recipe_count
        FROM shopping_list_items
        WHERE shopping_list_id = $1
        ORDER BY created_at ASC, ingredient_name ASC
        """,
        shopping_list_id,
    )
    return ShoppingListResponse(
        id=str(shopping_list["id"]),
        user_id=str(shopping_list["user_id"]),
        start_date=str(shopping_list["start_date"]),
        end_date=str(shopping_list["end_date"]),
        items=[
            ShoppingListItemResponse(
                id=str(item["id"]),
                ingredient_name=item["ingredient_name"],
                quantity=item.get("quantity"),
                checked=item["checked"],
                source_recipe_count=item["source_recipe_count"],
            )
            for item in items
        ],
    )


# PUBLIC_INTERFACE
async def toggle_shopping_list_item_flow(item_id: str, checked: bool) -> str:
    """Update a shopping list item's checked state."""
    logger.info("toggle_shopping_list_item_flow_start item_id=%s checked=%s", item_id, checked)
    return await execute(
        "UPDATE shopping_list_items SET checked = $2 WHERE id = $1",
        item_id,
        checked,
    )


# PUBLIC_INTERFACE
async def add_custom_shopping_list_item_flow(shopping_list_id: str, ingredient_name: str, quantity: str | None) -> ShoppingListItemResponse:
    """Add a custom shopping list item."""
    logger.info("add_custom_shopping_list_item_flow_start shopping_list_id=%s", shopping_list_id)
    item = await fetch_one(
        """
        INSERT INTO shopping_list_items (shopping_list_id, ingredient_name, quantity, checked, source_recipe_count)
        VALUES ($1, $2, $3, FALSE, 0)
        RETURNING id, ingredient_name, quantity, checked, source_recipe_count
        """,
        shopping_list_id,
        ingredient_name,
        quantity,
    )
    return ShoppingListItemResponse(
        id=str(item["id"]),
        ingredient_name=item["ingredient_name"],
        quantity=item.get("quantity"),
        checked=item["checked"],
        source_recipe_count=item["source_recipe_count"],
    )
