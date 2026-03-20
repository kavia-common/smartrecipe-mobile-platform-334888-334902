from collections.abc import Iterable
from typing import Any


# PUBLIC_INTERFACE
def build_limit_offset(limit: int, offset: int) -> tuple[int, int]:
    """Normalize pagination values."""
    normalized_limit = min(max(limit, 1), 100)
    normalized_offset = max(offset, 0)
    return normalized_limit, normalized_offset


# PUBLIC_INTERFACE
def ensure_list(value: Any) -> list[Any]:
    """Normalize nullable iterable values into lists."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple | set):
        return list(value)
    if isinstance(value, str):
        return [value]
    if isinstance(value, Iterable):
        return list(value)
    return [value]
