from pydantic import BaseModel, Field


class ShoppingListGenerateRequest(BaseModel):
    """Generate shopping list request."""

    user_id: str = Field(..., description="User identifier.")
    start_date: str = Field(..., description="Inclusive meal plan start date in ISO format.")
    end_date: str = Field(..., description="Inclusive meal plan end date in ISO format.")


class ShoppingListItemResponse(BaseModel):
    """Shopping list item representation."""

    id: str = Field(..., description="Shopping list item identifier.")
    ingredient_name: str = Field(..., description="Ingredient name.")
    quantity: str | None = Field(default=None, description="Aggregated quantity text.")
    checked: bool = Field(default=False, description="Whether the item is checked off.")
    source_recipe_count: int = Field(default=0, description="Number of source recipes contributing to the item.")


class ShoppingListResponse(BaseModel):
    """Shopping list response."""

    id: str = Field(..., description="Shopping list identifier.")
    user_id: str = Field(..., description="Owner user identifier.")
    start_date: str = Field(..., description="Inclusive source start date.")
    end_date: str = Field(..., description="Inclusive source end date.")
    items: list[ShoppingListItemResponse] = Field(..., description="Shopping list items.")
