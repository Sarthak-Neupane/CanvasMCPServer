"""Generic list wrapper for MCP tool responses."""

from __future__ import annotations

from typing import Generic, List, Sequence, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ListResult(BaseModel, Generic[T]):
    """
    Normalized list response for MCP tools.

    Replaces bare JSON arrays so agents receive an explicit count and whether
    pagination caps may have omitted additional Canvas items.
    """

    results: List[T] = Field(description="Items returned for this tool call")
    result_count: int = Field(
        description="Number of items in results (equals len(results))",
    )
    truncated: bool = Field(
        default=False,
        description=(
            "True when more items may exist on Canvas but were not fetched "
            "due to server pagination limits or an explicit result cap"
        ),
    )

    @classmethod
    def from_items(
        cls,
        items: Sequence[T],
        *,
        truncated: bool = False,
    ) -> "ListResult[T]":
        materialized = list(items)
        return cls(
            results=materialized,
            result_count=len(materialized),
            truncated=truncated,
        )
