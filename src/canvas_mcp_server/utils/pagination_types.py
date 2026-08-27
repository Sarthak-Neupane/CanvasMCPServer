"""Shared types for paginated Canvas API collection fetches."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, List, TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class PaginatedResult(Generic[T]):
    """Items collected from one or more Canvas list/connection pages."""

    items: List[T]
    truncated: bool = False
