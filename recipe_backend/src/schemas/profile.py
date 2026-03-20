from pydantic import BaseModel, EmailStr, Field


class DietaryPreferences(BaseModel):
    """Dietary and allergy preference model."""

    diets: list[str] = Field(default_factory=list, description="Selected diet preference identifiers.")
    allergens: list[str] = Field(default_factory=list, description="Known allergens to exclude.")
    disliked_ingredients: list[str] = Field(default_factory=list, description="Ingredients to avoid.")


class UserProfileResponse(BaseModel):
    """Profile response model."""

    id: str = Field(..., description="User identifier.")
    email: EmailStr = Field(..., description="User email address.")
    full_name: str | None = Field(default=None, description="User display name.")
    preferences: DietaryPreferences = Field(..., description="Dietary preferences.")
    is_admin: bool = Field(default=False, description="Whether the user has admin access.")


class UpdateProfileRequest(BaseModel):
    """Profile update request."""

    full_name: str | None = Field(default=None, description="Updated display name.")
    diets: list[str] = Field(default_factory=list, description="Updated diet identifiers.")
    allergens: list[str] = Field(default_factory=list, description="Updated allergen identifiers.")
    disliked_ingredients: list[str] = Field(default_factory=list, description="Updated avoided ingredients.")
