"""Helpers for building normalized list tool responses."""

from __future__ import annotations

from typing import Sequence, TypeVar

from ..models.common.list_result_model import ListResult

T = TypeVar("T")


def list_result(
    items: Sequence[T],
    *,
    truncated: bool = False,
) -> ListResult[T]:
    """Wrap tool list output with result_count and truncation metadata."""
    return ListResult.from_items(items, truncated=truncated)
