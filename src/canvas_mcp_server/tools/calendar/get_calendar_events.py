"""Tool for listing Canvas calendar events via the REST API.

Uses GET /api/v1/calendar_events (events and assignment due dates).
"""

from typing import Final, List, Dict, Any, Optional, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import CalendarEvent, ListResult
from ...utils.list_results import list_result
from ...errors import as_tool_error
from ...utils import canvas_api_client
from ._parse import calendar_event_from_api

CalendarEventsResponse: TypeAlias = Union[ListResult[CalendarEvent], Dict[str, Any]]

REST_ENDPOINT = "v1/calendar_events"
DASHBOARD_ENDPOINT = "v1/dashboard/dashboard_cards"
MAX_CONTEXT_CODES = 10
EVENT_TYPES = ("event", "assignment")


async def _dashboard_context_codes() -> List[str]:
    """Course context codes from the user's dashboard (Canvas caps at 10)."""
    response = await canvas_api_client.get_rest(endpoint=DASHBOARD_ENDPOINT)
    cards = response.data
    if not isinstance(cards, list):
        raise Exception("Canvas dashboard_cards response was not a list")

    codes: List[str] = []
    for card in cards:
        if not isinstance(card, dict) or "id" not in card:
            continue
        codes.append(f"course_{card['id']}")
        if len(codes) >= MAX_CONTEXT_CODES:
            break
    return codes


async def _fetch_calendar_events(
    *,
    event_type: str,
    start_date: Optional[str],
    end_date: Optional[str],
    context_codes: List[str],
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
            )
            events.extend(batch)
            truncated = truncated or batch_truncated

        events.sort(
            key=lambda item: (
                item.start_at is None,
                item.start_at or item.all_day_date or "",
            )
        )
        return list_result(events, truncated=truncated)

    except Exception as e:
        return as_tool_error(e, source="canvas_rest")


get_calendar_events_tool: Final[Tool] = Tool.from_function(
    name="get_calendar_events",
    description=(
        "List Canvas calendar events and assignment due dates with optional "
        "start_date, end_date, and course_id filters."
    ),
    fn=get_calendar_events,
)
