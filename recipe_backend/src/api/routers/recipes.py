from fastapi import APIRouter, Query, status

from src.schemas.common import MessageResponse
from src.schemas.recipes import (
    CollectionCreateRequest,
    CollectionRecipeRequest,
    CollectionResponse,
    FavoriteMutationRequest,
    RecipeDetail,
    RecipeSearchResponse,
    RecipeSummary,
)
from src.services.recipe_service import (
    add_favorite_flow,
    add_recipe_to_collection_flow,
    create_collection_flow,
    get_recipe_detail_flow,
    list_collections_flow,
    list_favorites_flow,
    remove_favorite_flow,
    remove_recipe_from_collection_flow,
    search_recipes_flow,
)

router = APIRouter(tags=["recipes"])


# PUBLIC_INTERFACE
@router.get(
    "/recipes",
    response_model=RecipeSearchResponse,
    summary="Search recipes",
    description=(
        "Search and filter recipes by text query, cuisine, difficulty, total time, diets, allergens, "
        "and included ingredients."
    ),
    operation_id="searchRecipes",
)
async def search_recipes(
    query: str | None = Query(default=None, description="Search text matching title or description."),
    cuisine: str | None = Query(default=None, description="Cuisine filter."),
    difficulty: str | None = Query(default=None, description="Difficulty filter."),
    max_total_time: int | None = Query(default=None, ge=0, description="Maximum combined prep and cook time."),
    diets: list[str] = Query(default_factory=list, description="Diet filters."),
    allergens: list[str] = Query(default_factory=list, description="Allergens to exclude."),
    ingredients: list[str] = Query(default_factory=list, description="Required ingredient names."),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum records to return."),
    offset: int = Query(default=0, ge=0, description="Records to skip before returning items."),
) -> RecipeSearchResponse:
    """Search recipes using the reusable recipe discovery flow."""
    return await search_recipes_flow(query, cuisine, difficulty, max_total_time, diets, allergens, ingredients, limit, offset)


# PUBLIC_INTERFACE
@router.get(
    "/recipes/{recipe_id}",
    response_model=RecipeDetail,
    summary="Get recipe detail",
    description="Return the detailed recipe payload with ingredients, steps, images, nutrition, and tags.",
    operation_id="getRecipeDetail",
)
async def get_recipe_detail(recipe_id: str) -> RecipeDetail:
    """Return a detailed recipe document."""
    return await get_recipe_detail_flow(recipe_id)


favorites_router = APIRouter(prefix="/favorites", tags=["favorites"])
collections_router = APIRouter(prefix="/collections", tags=["favorites"])


# PUBLIC_INTERFACE
@favorites_router.get(
    "/{user_id}",
    response_model=list[RecipeSummary],
    summary="List favorite recipes",
    description="Return all recipes favorited by the specified user.",
    operation_id="listFavorites",
)
async def list_favorites(user_id: str) -> list[RecipeSummary]:
    """List the user's favorite recipes."""
    return await list_favorites_flow(user_id)


# PUBLIC_INTERFACE
@favorites_router.post(
    "",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Favorite a recipe",
    description="Add a recipe to the specified user's favorites.",
    operation_id="addFavorite",
)
async def add_favorite(request: FavoriteMutationRequest) -> MessageResponse:
    """Add a recipe to the user's favorites."""
    await add_favorite_flow(request.user_id, request.recipe_id)
    return MessageResponse(message="Recipe added to favorites")


# PUBLIC_INTERFACE
@favorites_router.delete(
    "",
    response_model=MessageResponse,
    summary="Remove a favorite",
    description="Remove a recipe from the specified user's favorites.",
    operation_id="removeFavorite",
)
async def remove_favorite(request: FavoriteMutationRequest) -> MessageResponse:
    """Remove a recipe from the user's favorites."""
    await remove_favorite_flow(request.user_id, request.recipe_id)
    return MessageResponse(message="Recipe removed from favorites")


# PUBLIC_INTERFACE
@collections_router.get(
    "/{user_id}",
    response_model=list[CollectionResponse],
    summary="List collections",
    description="Return all collections created by the specified user.",
    operation_id="listCollections",
)
async def list_collections(user_id: str) -> list[CollectionResponse]:
    """List recipe collections for a user."""
    return await list_collections_flow(user_id)


# PUBLIC_INTERFACE
@collections_router.post(
    "",
    response_model=CollectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create collection",
    description="Create a new recipe collection for a user.",
    operation_id="createCollection",
)
async def create_collection(request: CollectionCreateRequest) -> CollectionResponse:
    """Create a new user collection."""
    return await create_collection_flow(request)


# PUBLIC_INTERFACE
@collections_router.post(
    "/{collection_id}/recipes",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add recipe to collection",
    description="Add a recipe to an existing collection.",
    operation_id="addRecipeToCollection",
)
async def add_recipe_to_collection(collection_id: str, request: CollectionRecipeRequest) -> MessageResponse:
    """Add a recipe to a collection."""
    await add_recipe_to_collection_flow(collection_id, request.recipe_id)
    return MessageResponse(message="Recipe added to collection")


# PUBLIC_INTERFACE
@collections_router.delete(
    "/{collection_id}/recipes/{recipe_id}",
    response_model=MessageResponse,
    summary="Remove recipe from collection",
    description="Remove a recipe from an existing collection.",
    operation_id="removeRecipeFromCollection",
)
async def remove_recipe_from_collection(collection_id: str, recipe_id: str) -> MessageResponse:
    """Remove a recipe from a collection."""
    await remove_recipe_from_collection_flow(collection_id, recipe_id)
    return MessageResponse(message="Recipe removed from collection")


router.include_router(favorites_router)
router.include_router(collections_router)
