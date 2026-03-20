from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Registration request model."""

    email: EmailStr = Field(..., description="User email address.")
    password: str = Field(..., min_length=8, description="User password.")
    full_name: str = Field(..., min_length=1, description="Display name for the account.")


class LoginRequest(BaseModel):
    """Login request model."""

    email: EmailStr = Field(..., description="User email address.")
    password: str = Field(..., min_length=8, description="User password.")


class AuthTokenResponse(BaseModel):
    """Authentication token response."""

    access_token: str = Field(..., description="Bearer access token.")
    token_type: str = Field(default="bearer", description="Token type.")
    user_id: str = Field(..., description="Authenticated user identifier.")
    email: EmailStr = Field(..., description="Authenticated email.")
