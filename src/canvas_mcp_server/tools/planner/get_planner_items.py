"""Tool for listing Canvas student planner items via the REST API.

Uses GET /api/v1/planner/items.
"""

from typing import Final, List, Dict, Any, Optional, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import PlannerItem
from ...errors import as_tool_error
from ...utils import canvas_api_client
from ._parse import planner_item_from_api

PlannerItemsResponse: TypeAlias = Union[List[PlannerItem], Dict[str, Any]]

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

        data = await canvas_api_client.get_rest_paginated(
            endpoint=REST_ENDPOINT,
            params=params,
        )

        return [planner_item_from_api(item) for item in data if isinstance(item, dict)]

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
