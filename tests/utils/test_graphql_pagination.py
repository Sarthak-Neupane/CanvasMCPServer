"""Tests for GraphQL connection pagination helpers."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import pytest

from canvas_mcp_server.utils.graphql_pagination import paginate_graphql_connection


@pytest.mark.asyncio
async def test_paginate_graphql_connection_follows_cursors() -> None:
    pages = [
        {
            "nodes": [{"_id": "1"}],
            "pageInfo": {"endCursor": "cursor1", "hasNextPage": True},
        },
        {
            "nodes": [{"_id": "2"}],
            "pageInfo": {"endCursor": "cursor2", "hasNextPage": False},
        },
    ]
    calls: List[Optional[str]] = []

    async def fetch_connection(after: Optional[str]) -> Dict[str, Any]:
        calls.append(after)
        index = 0 if after is None else 1
        return pages[index]

    nodes = await paginate_graphql_connection(fetch_connection, max_pages=5)

    assert [node["_id"] for node in nodes.items] == ["1", "2"]
    assert calls == [None, "cursor1"]


@pytest.mark.asyncio
async def test_paginate_graphql_connection_respects_max_items() -> None:
    async def fetch_connection(_after: Optional[str]) -> Dict[str, Any]:
        return {
            "nodes": [{"_id": "1"}, {"_id": "2"}, {"_id": "3"}],
            "pageInfo": {"hasNextPage": False},
        }

    nodes = await paginate_graphql_connection(
        fetch_connection,
        max_pages=5,
        max_items=2,
    )

    assert len(nodes.items) == 2
    assert nodes.truncated is True
