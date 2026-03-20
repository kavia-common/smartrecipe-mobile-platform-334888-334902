from typing import Any

from pydantic import BaseModel, Field


class RecipeSummary(BaseModel):
    """Compact recipe representation for list views."""

    id: str = Field(..., description="Recipe identifier.")
    title: str = Field(..., description="Recipe title.")
    description: str | None = Field(default=None, description="Short recipe summary.")
    cuisine: str | None = Field(default=None, description="Cuisine or regional category.")
    difficulty: str | None = Field(default=None, description="Difficulty label.")
    prep_time_minutes: int | None = Field(default=None, description="Preparation time in minutes.")
    cook_time_minutes: int | None = Field(default=None, description="Cooking time in minutes.")
    image_url: str | None = Field(default=None, description="Primary recipe image URL.")


class RecipeDetail(BaseModel):
    """Detailed recipe representation."""

    id: str = Field(..., description="Recipe identifier.")
    title: str = Field(..., description="Recipe title.")
    description: str | None = Field(default=None, description="Recipe summary.")
    cuisine: str | None = Field(default=None, description="Cuisine or regional category.")
    difficulty: str | None = Field(default=None, description="Difficulty label.")
    prep_time_minutes: int | None = Field(default=None, description="Preparation time in minutes.")
    cook_time_minutes: int | None = Field(default=None, description="Cooking time in minutes.")
    servings: int | None = Field(default=None, description="Default number of servings.")
    nutrition: dict[str, Any] = Field(default_factory=dict, description="Nutrition estimates.")
    ingredients: list[dict[str, Any]] = Field(default_factory=list, description="Ingredient rows.")
    steps: list[dict[str, Any]] = Field(default_factory=list, description="Preparation steps.")
    tags: list[str] = Field(default_factory=list, description="Recipe tags.")
    image_urls: list[str] = Field(default_factory=list, description="Recipe images.")


class RecipeSearchResponse(BaseModel):
    """Recipe search response wrapper."""

    items: list[RecipeSummary] = Field(..., description="Matching recipes.")
    total: int = Field(..., description="Total matching recipes.")


class FavoriteMutationRequest(BaseModel):
    """Request to favorite or unfavorite a recipe."""

    user_id: str = Field(..., description="User identifier.")
    recipe_id: str = Field(..., description="Recipe identifier.")


class CollectionCreateRequest(BaseModel):
    """Create collection request."""

    user_id: str = Field(..., description="User identifier.")
    name: str = Field(..., min_length=1, description="Collection name.")
    description: str | None = Field(default=None, description="Collection description.")


class CollectionRecipeRequest(BaseModel):
    """Collection membership mutation request."""

    recipe_id: str = Field(..., description="Recipe identifier.")


class CollectionResponse(BaseModel):
    """Collection response model."""

    id: str = Field(..., description="Collection identifier.")
    user_id: str = Field(..., description="Owner user identifier.")
    name: str = Field(..., description="Collection name.")
    description: str | None = Field(default=None, description="Collection description.")
    recipe_count: int = Field(default=0, description="Number of recipes in the collection.")
