"""Shared limits for list-shaped MCP tool responses."""

from __future__ import annotations

from typing import Annotated, Sequence, TypeVar

from pydantic import Field

from .list_results import list_result
from ..models.common.list_result_model import ListResult

DEFAULT_LIST_LIMIT = 50
MAX_LIST_LIMIT = 100

ListLimitField = Annotated[
    int,
    Field(
        description=(
            "Maximum number of items to return. The response sets truncated=true "
            "when Canvas has more matching items."
        ),
        ge=1,
        le=MAX_LIST_LIMIT,
    ),
]

T = TypeVar("T")


def resolve_list_limit(limit: int) -> int:
    """Clamp a caller-provided limit to the supported range."""
    return min(max(1, limit), MAX_LIST_LIMIT)


def cap_items(
    items: Sequence[T],
    limit: int,
    *,
    truncated: bool = False,
) -> tuple[list[T], bool]:
    """Return at most ``limit`` items and whether the list was cut short."""
    if len(items) <= limit:
        return list(items), truncated
    return list(items[:limit]), True


def finalize_list(
    items: Sequence[T],
    limit: int,
    *,
    truncated: bool = False,
) -> ListResult[T]:
    """Apply a list cap and wrap as ``ListResult``."""
    capped, cut = cap_items(items, limit, truncated=truncated)
    return list_result(capped, truncated=truncated or cut)
