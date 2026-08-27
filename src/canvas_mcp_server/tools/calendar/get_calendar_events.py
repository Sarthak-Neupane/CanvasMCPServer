"""Tool for listing Canvas calendar events via the REST API.

Uses GET /api/v1/calendar_events (events and assignment due dates).
"""

from typing import Annotated, Any, Dict, Final, List, Optional, TypeAlias, Union

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...errors import as_tool_error
from ...models import CalendarEvent, ListResult
from ...utils import canvas_api_client
from ...utils.dashboard import dashboard_course_ids
from ...utils.list_limits import (
    DEFAULT_LIST_LIMIT,
    ListLimitField,
    finalize_list,
    resolve_list_limit,
)
from ._parse import calendar_event_from_api

CalendarEventsResponse: TypeAlias = Union[ListResult[CalendarEvent], Dict[str, Any]]

REST_ENDPOINT = "v1/calendar_events"
MAX_CONTEXT_CODES = 10
EVENT_TYPES = ("event", "assignment")


async def _dashboard_context_codes() -> List[str]:
    """Course context codes from the user's dashboard (Canvas caps at 10)."""
    ids = sorted(await dashboard_course_ids())
    return [f"course_{course_id}" for course_id in ids[:MAX_CONTEXT_CODES]]


async def _fetch_calendar_events(
    *,
    event_type: str,
    start_date: Optional[str],
    end_date: Optional[str],
    context_codes: List[str],
    max_items: Optional[int],
) -> tuple[List[CalendarEvent], bool]:
    params: Dict[str, Any] = {
        "type": event_type,
        "per_page": 100,
        "excludes[]": ["description", "child_events"],
    }
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    if context_codes:
        params["context_codes[]"] = context_codes

    paginated = await canvas_api_client.get_rest_paginated(
        endpoint=REST_ENDPOINT,
        params=params,
        max_items=max_items,
    )

    events = [
        calendar_event_from_api(item, event_type=event_type)
        for item in paginated.items
        if isinstance(item, dict)
    ]
    return events, paginated.truncated


async def get_calendar_events(
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
                "(context_codes[]=course_{id}). When omitted, uses dashboard "
                "courses (up to 10)."
            ),
        ),
    ] = None,
    limit: ListLimitField = DEFAULT_LIST_LIMIT,
) -> CalendarEventsResponse:
    """
    List calendar events and assignment due dates from Canvas.

    Fetches both custom calendar events and assignment due dates, merges
    them, and sorts by start_at. Without course_id, scopes to dashboard
    courses (Canvas allows at most 10 context codes per request).

    Returns an error object with "error", "message", and optionally
    "status_code" keys on failure.
    """
    try:
        item_limit = resolve_list_limit(limit)
        if course_id:
            context_codes = [f"course_{course_id}"]
        else:
            context_codes = await _dashboard_context_codes()

        events: List[CalendarEvent] = []
        truncated = False
        for event_type in EVENT_TYPES:
            batch, batch_truncated = await _fetch_calendar_events(
                event_type=event_type,
                start_date=start_date,
                end_date=end_date,
                context_codes=context_codes,
                max_items=item_limit,
            )
            events.extend(batch)
            truncated = truncated or batch_truncated

        events.sort(
            key=lambda item: (
                item.start_at is None,
                item.start_at or item.all_day_date or "",
            )
        )
        return finalize_list(events, item_limit, truncated=truncated)

    except Exception as e:
        return as_tool_error(e, source="canvas_rest")


get_calendar_events_tool: Final[Tool] = Tool.from_function(
    name="get_calendar_events",
    description=(
        "List Canvas calendar events and assignment due dates with optional "
        "start_date, end_date, and course_id filters. Use limit to cap results."
    ),
    fn=get_calendar_events,
)
