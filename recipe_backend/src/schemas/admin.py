from typing import Any

from pydantic import BaseModel, Field


class AdminRecipeUpsertRequest(BaseModel):
    """Admin recipe upsert request."""

    title: str = Field(..., min_length=1, description="Recipe title.")
    description: str | None = Field(default=None, description="Recipe summary.")
    cuisine: str | None = Field(default=None, description="Cuisine label.")
    difficulty: str | None = Field(default=None, description="Difficulty label.")
    prep_time_minutes: int | None = Field(default=None, ge=0, description="Preparation time.")
    cook_time_minutes: int | None = Field(default=None, ge=0, description="Cooking time.")
    servings: int | None = Field(default=None, ge=1, description="Default servings.")
    nutrition: dict[str, Any] = Field(default_factory=dict, description="Nutrition estimates.")
    tags: list[str] = Field(default_factory=list, description="Tag names.")
    ingredients: list[dict[str, Any]] = Field(default_factory=list, description="Ingredient payloads.")
    steps: list[dict[str, Any]] = Field(default_factory=list, description="Step payloads.")
    image_urls: list[str] = Field(default_factory=list, description="Image URLs.")


class AdminTagRequest(BaseModel):
    """Admin tag create request."""

    name: str = Field(..., min_length=1, description="Tag name.")
    category: str | None = Field(default=None, description="Tag category.")
