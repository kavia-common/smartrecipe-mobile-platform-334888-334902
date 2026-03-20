from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers.admin import router as admin_router
from src.api.routers.analytics import router as analytics_router
from src.api.routers.auth import router as auth_router
from src.api.routers.cooking import router as cooking_router
from src.api.routers.meal_plans import router as meal_plan_router
from src.api.routers.profile import router as profile_router
from src.api.routers.recipes import router as recipe_router
from src.api.routers.shopping_lists import router as shopping_list_router
from src.core.config import get_settings
from src.core.database import close_database_pool, initialize_database_pool
from src.core.logging import get_logger
from src.schemas.common import HealthResponse

logger = get_logger("app")
settings = get_settings()

openapi_tags = [
    {"name": "system", "description": "System health and API metadata endpoints."},
    {"name": "auth", "description": "Authentication and session management."},
    {"name": "recipes", "description": "Recipe discovery, search, filtering, and details."},
    {"name": "favorites", "description": "Favorite recipes and user collections."},
    {"name": "cooking", "description": "Cooking mode helpers, timers, and serving scaling."},
    {"name": "meal-plans", "description": "Weekly meal planning and slot management."},
    {"name": "shopping-lists", "description": "Generated and editable shopping lists."},
    {"name": "profile", "description": "Profile, dietary preferences, and sync settings."},
    {"name": "admin", "description": "Admin content management for recipes and taxonomy."},
    {"name": "analytics", "description": "Analytics event ingestion endpoints."},
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Manage application startup and shutdown resources."""
    await initialize_database_pool()
    logger.info("application_started")
    try:
        yield
    finally:
        await close_database_pool()
        logger.info("application_stopped")


app = FastAPI(
    title="SmartRecipe Backend API",
    description=(
        "Backend API for the SmartRecipe mobile-first recipe application. "
        "Provides authentication, recipe discovery, favorites and collections, "
        "cooking helpers, meal planning, shopping list generation, profile management, "
        "admin content management, and analytics ingestion."
    ),
    version="1.0.0",
    openapi_tags=openapi_tags,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# PUBLIC_INTERFACE
@app.get(
    "/",
    response_model=HealthResponse,
    tags=["system"],
    summary="Health check",
    description="Return API health information and service metadata.",
    operation_id="getHealthStatus",
)
async def health_check() -> HealthResponse:
    """Return health information for monitoring and readiness checks."""
    return HealthResponse(status="ok", service="recipe_backend", version=app.version)


# PUBLIC_INTERFACE
@app.get(
    "/docs/websocket",
    tags=["system"],
    summary="WebSocket usage guide",
    description=(
        "Provide usage guidance for future real-time sync channels. "
        "This backend currently exposes REST APIs and reserves WebSocket integration "
        "for live sync workflows such as collaborative meal planning and timer updates."
    ),
    operation_id="getWebSocketUsageGuide",
)
async def websocket_usage_guide() -> dict[str, str]:
    """Return documentation for the planned WebSocket interface."""
    return {
        "status": "not_enabled",
        "message": (
            "WebSocket sync endpoints are reserved for future real-time device sync. "
            "Use the REST APIs documented in /docs and /openapi.json for current integrations."
        ),
    }


app.include_router(auth_router)
app.include_router(recipe_router)
app.include_router(cooking_router)
app.include_router(meal_plan_router)
app.include_router(shopping_list_router)
app.include_router(profile_router)
app.include_router(admin_router)
app.include_router(analytics_router)
