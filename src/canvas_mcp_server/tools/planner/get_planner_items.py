"""Tool for listing Canvas student planner items via the REST API.

Uses GET /api/v1/planner/items.
"""

from typing import Final, List, Dict, Any, Optional, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import PlannerItem, ListResult
from ...utils.list_limits import DEFAULT_LIST_LIMIT, ListLimitField, finalize_list, resolve_list_limit
from ...errors import as_tool_error
from ...utils import canvas_api_client
from ._parse import planner_item_from_api

PlannerItemsResponse: TypeAlias = Union[ListResult[PlannerItem], Dict[str, Any]]

REST_ENDPOINT = "v1/planner/items"


async def get_planner_items(
    start_date: Annotated[
        Optional[str],
        Field(
            description=(
                "Inclusive start date (yyyy-mm-dd or ISO-8601), e.g. '2026-08-27'."
            ),
        ),
    ] = None,
    end_date: Annotated[
        Optional[str],
        Field(
            description=(
                "Inclusive end date (yyyy-mm-dd or ISO-8601), e.g. '2026-09-03'."
            ),
        ),
    ] = None,
    course_id: Annotated[
        Optional[str],
        Field(
            description=(
                "Optional course id to limit results to one course "
                "(context_codes[]=course_{id})."
            ),
        ),
    ] = None,
    limit: ListLimitField = DEFAULT_LIST_LIMIT,
) -> PlannerItemsResponse:
    """
    List items on the Canvas student planner.

    Returns assignments, quizzes, discussions, pages, notes, and other
    planner entries with normalized types, titles, due/todo dates, and
    submission flags when available.

    Returns an error object with "error", "message", and optionally
    "status_code" keys on failure.
    """
    try:
        params: Dict[str, Any] = {"per_page": 100}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if course_id:
            params["context_codes[]"] = f"course_{course_id}"

        item_limit = resolve_list_limit(limit)
        paginated = await canvas_api_client.get_rest_paginated(
            endpoint=REST_ENDPOINT,
            params=params,
            max_items=item_limit,
        )

        items = [planner_item_from_api(item) for item in paginated.items if isinstance(item, dict)]
        return finalize_list(items, item_limit, truncated=paginated.truncated)

    except Exception as e:
        return as_tool_error(e, source="canvas_rest")


get_planner_items_tool: Final[Tool] = Tool.from_function(
    name="get_planner_items",
    description=(
        "List Canvas student planner items (assignments, quizzes, discussions, "
        "pages, notes, etc.) with normalized types and due dates. Optional "
        "start_date, end_date, and course_id filters."
    ),
    fn=get_planner_items,
)
