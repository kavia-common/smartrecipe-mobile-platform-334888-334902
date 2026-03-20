import base64
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status

from src.core.config import get_settings
from src.core.database import execute, fetch_one
from src.core.logging import get_logger
from src.schemas.auth import AuthTokenResponse, LoginRequest, RegisterRequest

logger = get_logger("auth_service")


def _encode_token(payload: str) -> str:
    """Encode a lightweight token payload for the current scaffold."""
    return base64.urlsafe_b64encode(payload.encode("utf-8")).decode("utf-8")


# PUBLIC_INTERFACE
async def register_user_flow(request: RegisterRequest) -> AuthTokenResponse:
    """Create a user account and return an access token."""
    logger.info("register_user_flow_start email=%s", request.email)
    existing_user = await fetch_one("SELECT id, email FROM users WHERE email = $1", request.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    inserted_user = await fetch_one(
        """
        INSERT INTO users (email, password_hash, full_name)
        VALUES ($1, crypt($2, gen_salt('bf')), $3)
        RETURNING id, email
        """,
        request.email,
        request.password,
        request.full_name,
    )
    if inserted_user is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User could not be created")

    token = _encode_token(f"{inserted_user['id']}|{request.email}|{datetime.now(UTC).isoformat()}")
    logger.info("register_user_flow_success user_id=%s", inserted_user["id"])
    return AuthTokenResponse(
        access_token=token,
        user_id=str(inserted_user["id"]),
        email=inserted_user["email"],
    )


# PUBLIC_INTERFACE
async def login_user_flow(request: LoginRequest) -> AuthTokenResponse:
    """Authenticate a user and return an access token."""
    logger.info("login_user_flow_start email=%s", request.email)
    user = await fetch_one(
        """
        SELECT id, email
        FROM users
        WHERE email = $1
          AND password_hash = crypt($2, password_hash)
        """,
        request.email,
        request.password,
    )
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    settings = get_settings()
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_expiry_minutes)
    token = _encode_token(f"{user['id']}|{user['email']}|{expires_at.isoformat()}")
    logger.info("login_user_flow_success user_id=%s", user["id"])
    return AuthTokenResponse(
        access_token=token,
        user_id=str(user["id"]),
        email=user["email"],
    )


# PUBLIC_INTERFACE
async def create_guest_user_flow(email: str, full_name: str) -> str:
    """Create a lightweight guest-style user record for seed or migration scenarios."""
    logger.info("create_guest_user_flow_start email=%s", email)
    status_message = await execute(
        """
        INSERT INTO users (email, full_name)
        VALUES ($1, $2)
        ON CONFLICT (email) DO UPDATE SET full_name = EXCLUDED.full_name
        """,
        email,
        full_name,
    )
    logger.info("create_guest_user_flow_complete status=%s", status_message)
    return status_message
