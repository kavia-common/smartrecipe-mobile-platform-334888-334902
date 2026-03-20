from fastapi import APIRouter, status

from src.schemas.admin import AdminRecipeUpsertRequest, AdminTagRequest

from src.services.admin_service import create_tag_flow, delete_recipe_flow, list_tags_flow, upsert_recipe_flow

router = APIRouter(prefix="/admin", tags=["admin"])


# PUBLIC_INTERFACE
@router.post(
    "/recipes",
    response_model=dict[str, str],
    status_code=status.HTTP_201_CREATED,
    summary="Create recipe",
    description="Create a recipe and its related ingredients, steps, images, and tags.",
    operation_id="createAdminRecipe",
)
async def create_recipe(request: AdminRecipeUpsertRequest) -> dict[str, str]:
    """Create a recipe from the admin dashboard."""
    return await upsert_recipe_flow(None, request)


# PUBLIC_INTERFACE
@router.put(
    "/recipes/{recipe_id}",
    response_model=dict[str, str],
    summary="Update recipe",
    description="Update a recipe and fully replace its related ingredients, steps, images, and tags.",
    operation_id="updateAdminRecipe",
)
async def update_recipe(recipe_id: str, request: AdminRecipeUpsertRequest) -> dict[str, str]:
    """Update a recipe from the admin dashboard."""
    return await upsert_recipe_flow(recipe_id, request)


# PUBLIC_INTERFACE
@router.delete(
    "/recipes/{recipe_id}",
    response_model=dict[str, str],
    summary="Delete recipe",
    description="Delete a recipe from the admin dashboard.",
    operation_id="deleteAdminRecipe",
)
async def delete_recipe(recipe_id: str) -> dict[str, str]:
    """Delete a recipe."""
    await delete_recipe_flow(recipe_id)
    return {"message": "Recipe deleted"}


# PUBLIC_INTERFACE
@router.get(
    "/tags",
    response_model=list[dict[str, str | None]],
    summary="List tags",
    description="Return all taxonomy tags for admin management.",
    operation_id="listAdminTags",
)
async def list_tags() -> list[dict[str, str | None]]:
    """Return all tags."""
    return await list_tags_flow()


# PUBLIC_INTERFACE
@router.post(
    "/tags",
    response_model=dict[str, str],
    status_code=status.HTTP_201_CREATED,
    summary="Create or update tag",
    description="Create or update a taxonomy tag for recipes.",
    operation_id="createAdminTag",
)
async def create_tag(request: AdminTagRequest) -> dict[str, str]:
    """Create or update a tag."""
    return await create_tag_flow(request)
