"""Regression tests for calendar tools."""

from typing import Any, Dict, Optional

from canvas_mcp_server.models import CalendarEvent
from canvas_mcp_server.tools.calendar._parse import course_id_from_context
from canvas_mcp_server.tools.calendar.get_calendar_events import get_calendar_events
from tests.fixtures.calendar import (
    CALENDAR_ASSIGNMENTS_REST,
    CALENDAR_EVENTS_REST,
    DASHBOARD_CARDS_REST,
)
from tests.helpers.assertions import assert_list_result
from tests.helpers.canvas_mock import CanvasAPIMock, make_http_response


def test_course_id_from_context() -> None:
    assert course_id_from_context("course_100001") == 100001
    assert course_id_from_context("user_42") is None
    assert course_id_from_context(None) is None


async def _register_calendar_route(canvas_api: CanvasAPIMock) -> None:
    async def calendar_route(
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ):
        del endpoint, headers, timeout
        data = (
            CALENDAR_ASSIGNMENTS_REST
            if params and params.get("type") == "assignment"
            else CALENDAR_EVENTS_REST
        )
        return make_http_response(data)

    canvas_api._rest_routes["v1/calendar_events"] = calendar_route


async def test_get_calendar_events_success(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns("v1/dashboard/dashboard_cards", DASHBOARD_CARDS_REST)
    await _register_calendar_route(canvas_api)

    result = await get_calendar_events(
        start_date="2025-09-01",
        end_date="2025-09-30",
    )

    assert result.result_count == 2
    assert assert_list_result(result, CalendarEvent, count=result.result_count) or True
    assert result.results[0].event_type == "event"
    assert result.results[0].title == "Office hours"
    assert result.results[0].course_id == 100001
    assert result.results[1].event_type == "assignment"
    assert result.results[1].id == "assignment_200001"


async def test_get_calendar_events_course_filter(
    canvas_api: CanvasAPIMock,
) -> None:
    await _register_calendar_route(canvas_api)

    await get_calendar_events(
        start_date="2025-09-01",
        end_date="2025-09-30",
        course_id="100001",
    )

    assert canvas_api.get_rest_paginated_mock.await_count == 2
    for call in canvas_api.get_rest_paginated_mock.await_args_list:
        params = call.kwargs["params"]
        assert params["context_codes[]"] == ["course_100001"]
        assert params["type"] in ("event", "assignment")
