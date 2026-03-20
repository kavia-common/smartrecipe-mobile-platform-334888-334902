from fastapi import APIRouter, status

from src.schemas.auth import AuthTokenResponse, LoginRequest, RegisterRequest
from src.services.auth_service import login_user_flow, register_user_flow

router = APIRouter(prefix="/auth", tags=["auth"])


# PUBLIC_INTERFACE
@router.post(
    "/register",
    response_model=AuthTokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create an account using email and password, then return a bearer token.",
    operation_id="registerUser",
)
async def register(request: RegisterRequest) -> AuthTokenResponse:
    """Create a new user account and return an access token."""
    return await register_user_flow(request)


# PUBLIC_INTERFACE
@router.post(
    "/login",
    response_model=AuthTokenResponse,
    summary="Authenticate a user",
    description="Authenticate a user by email and password and return a bearer token.",
    operation_id="loginUser",
)
async def login(request: LoginRequest) -> AuthTokenResponse:
    """Authenticate a user and return an access token."""
    return await login_user_flow(request)
