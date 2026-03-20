from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = Field(default="development", alias="APP_ENV")
    app_debug: bool = Field(default=False, alias="APP_DEBUG")
    allowed_origins: str = Field(default="*", alias="ALLOWED_ORIGINS")

    postgres_url: str | None = Field(default=None, alias="POSTGRES_URL")
    postgres_user: str | None = Field(default=None, alias="POSTGRES_USER")
    postgres_password: str | None = Field(default=None, alias="POSTGRES_PASSWORD")
    postgres_db: str | None = Field(default=None, alias="POSTGRES_DB")
    postgres_port: int | None = Field(default=None, alias="POSTGRES_PORT")
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")

    jwt_secret: str = Field(default="development-secret", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expiry_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRY_MINUTES")

    analytics_source: str = Field(default="recipe_frontend", alias="ANALYTICS_SOURCE")

    @property
    def database_dsn(self) -> str:
        """Return the PostgreSQL DSN built from the available environment variables."""
        if self.postgres_url:
            return self.postgres_url

        user = self.postgres_user or "appuser"
        password = self.postgres_password or ""
        database = self.postgres_db or "myapp"
        port = self.postgres_port or 5432
        credentials = f"{user}:{password}@" if password else f"{user}@"
        return f"postgresql://{credentials}{self.postgres_host}:{port}/{database}"

    @property
    def allowed_origins_list(self) -> list[str]:
        """Return allowed CORS origins as a normalized list."""
        if self.allowed_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def cors_allow_credentials(self) -> bool:
        """Return whether credentialed CORS should be enabled for the configured origins."""
        return "*" not in self.allowed_origins_list

    @property
    def normalized_cors_origins(self) -> list[str]:
        """Return safe CORS origins for FastAPI middleware configuration.

        Contract:
        - Input: raw ALLOWED_ORIGINS environment variable.
        - Output: explicit origins list suitable for CORSMiddleware.
        - Invariant: when credentials are allowed, the list never contains a wildcard.
        """
        if self.cors_allow_credentials:
            return self.allowed_origins_list
        return ["*"]


# PUBLIC_INTERFACE
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
