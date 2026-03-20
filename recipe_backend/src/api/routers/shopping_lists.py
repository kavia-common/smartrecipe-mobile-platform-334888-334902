from pydantic import BaseModel, Field
from fastapi import APIRouter, status

from src.schemas.shopping_lists import (
    ShoppingListGenerateRequest,
    ShoppingListItemResponse,
    ShoppingListResponse,
)
from src.services.shopping_list_service import (
    add_custom_shopping_list_item_flow,
    generate_shopping_list_flow,
    get_shopping_list_flow,
    toggle_shopping_list_item_flow,
)

router = APIRouter(prefix="/shopping-lists", tags=["shopping-lists"])


class ShoppingListItemToggleRequest(BaseModel):
    """Toggle shopping list item check state request."""

    checked: bool = Field(..., description="Whether the shopping list item is checked off.")


class ShoppingListCustomItemRequest(BaseModel):
    """Add custom shopping list item request."""

    ingredient_name: str = Field(..., description="Ingredient or custom item name.")
    quantity: str | None = Field(default=None, description="Optional quantity text.")


# PUBLIC_INTERFACE
@router.post(
    "/generate",
    response_model=ShoppingListResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate shopping list",
    description="Generate a shopping list from meal plan items in the requested date range.",
    operation_id="generateShoppingList",
)
async def generate_shopping_list(request: ShoppingListGenerateRequest) -> ShoppingListResponse:
    """Generate a shopping list from planned meals."""
    return await generate_shopping_list_flow(request)


# PUBLIC_INTERFACE
@router.get(
    "/{shopping_list_id}",
    response_model=ShoppingListResponse,
    summary="Get shopping list",
    description="Return a shopping list and all of its items.",
    operation_id="getShoppingList",
)
async def get_shopping_list(shopping_list_id: str) -> ShoppingListResponse:
    """Return a shopping list."""
    return await get_shopping_list_flow(shopping_list_id)


# PUBLIC_INTERFACE
@router.patch(
    "/items/{item_id}",
    response_model=dict[str, str],
    summary="Update shopping list item state",
    description="Update the checked state of a shopping list item.",
    operation_id="toggleShoppingListItem",
)
async def toggle_shopping_list_item(item_id: str, request: ShoppingListItemToggleRequest) -> dict[str, str]:
    """Update a shopping list item's checked state."""
    await toggle_shopping_list_item_flow(item_id, request.checked)
    return {"message": "Shopping list item updated"}


# PUBLIC_INTERFACE
@router.post(
    "/{shopping_list_id}/items",
    response_model=ShoppingListItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add custom shopping list item",
    description="Append a custom item to a shopping list.",
    operation_id="addCustomShoppingListItem",
)
async def add_custom_item(shopping_list_id: str, request: ShoppingListCustomItemRequest) -> ShoppingListItemResponse:
    """Add a custom item to a shopping list."""
    return await add_custom_shopping_list_item_flow(shopping_list_id, request.ingredient_name, request.quantity)
