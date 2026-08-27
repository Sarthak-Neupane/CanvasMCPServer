"""Helpers for Canvas GraphQL Relay connection pagination."""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, List, Mapping, Optional

DEFAULT_GRAPHQL_PAGE_SIZE = 50
DEFAULT_GRAPHQL_MAX_PAGES = 10

FetchConnection = Callable[[Optional[str]], Awaitable[Mapping[str, Any]]]


async def paginate_graphql_connection(
    fetch_connection: FetchConnection,
    *,
    max_pages: int = DEFAULT_GRAPHQL_MAX_PAGES,
    max_items: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Aggregate nodes from a GraphQL connection across cursor pages.

    ``fetch_connection(after)`` must return a connection dict with ``nodes`` and
    optional ``pageInfo { endCursor, hasNextPage }``.
    """
    nodes: List[Dict[str, Any]] = []
    after: Optional[str] = None

    for _ in range(max_pages):
        connection = await fetch_connection(after)
        page_nodes = connection.get("nodes") or []
        for node in page_nodes:
            if isinstance(node, dict):
                nodes.append(node)

        if max_items is not None and len(nodes) >= max_items:
            return nodes[:max_items]

        page_info = connection.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break

        after = page_info.get("endCursor")
        if not after:
            break

    return nodes
