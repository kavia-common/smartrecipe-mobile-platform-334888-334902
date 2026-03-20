from __future__ import annotations

from typing import Any

import asyncpg

from src.core.config import get_settings
from src.core.logging import get_logger

logger = get_logger("database")
_pool: asyncpg.Pool | None = None


# PUBLIC_INTERFACE
async def initialize_database_pool() -> None:
    """Initialize the shared PostgreSQL connection pool."""
    global _pool
    if _pool is not None:
        return

    settings = get_settings()
    logger.info("database_pool_initializing dsn=%s", settings.database_dsn)
    _pool = await asyncpg.create_pool(
        dsn=settings.database_dsn,
        min_size=1,
        max_size=10,
        command_timeout=30,
    )
    logger.info("database_pool_ready")


# PUBLIC_INTERFACE
async def close_database_pool() -> None:
    """Close the shared PostgreSQL connection pool."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("database_pool_closed")


async def _get_pool() -> asyncpg.Pool:
    """Return the initialized connection pool."""
    if _pool is None:
        await initialize_database_pool()
    if _pool is None:
        raise RuntimeError("Database pool could not be initialized")
    return _pool


# PUBLIC_INTERFACE
async def fetch_all(query: str, *args: Any) -> list[dict[str, Any]]:
    """Execute a query and return all rows as dictionaries."""
    pool = await _get_pool()
    async with pool.acquire() as connection:
        rows = await connection.fetch(query, *args)
    return [dict(row) for row in rows]


# PUBLIC_INTERFACE
async def fetch_one(query: str, *args: Any) -> dict[str, Any] | None:
    """Execute a query and return a single row as a dictionary if present."""
    pool = await _get_pool()
    async with pool.acquire() as connection:
        row = await connection.fetchrow(query, *args)
    return dict(row) if row is not None else None


# PUBLIC_INTERFACE
async def execute(query: str, *args: Any) -> str:
    """Execute a statement and return the database status message."""
    pool = await _get_pool()
    async with pool.acquire() as connection:
        return await connection.execute(query, *args)
