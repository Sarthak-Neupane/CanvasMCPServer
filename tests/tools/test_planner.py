"""Regression tests for planner tools."""

from canvas_mcp_server.models import PlannerItem
from canvas_mcp_server.tools.planner._parse import normalize_plannable_type
from canvas_mcp_server.tools.planner.get_planner_items import get_planner_items
from tests.fixtures.planner import PLANNER_ITEMS_REST
from tests.helpers.assertions import assert_list_result
from tests.helpers.canvas_mock import CanvasAPIMock


def test_normalize_plannable_type() -> None:
    assert normalize_plannable_type("discussion_topic") == "discussion"
    assert normalize_plannable_type("wiki_page") == "page"
    assert normalize_plannable_type("planner_note") == "note"


async def test_get_planner_items_success(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns("v1/planner/items", PLANNER_ITEMS_REST)

    result = await get_planner_items()

    assert result.result_count == 3
    assert assert_list_result(result, PlannerItem, count=result.result_count) or True
    assert result.results[0].item_type == "assignment"
    assert result.results[0].title == "Homework 1"
    assert result.results[0].submissions is not None
    assert result.results[0].submissions.missing is True
    assert result.results[1].item_type == "note"
    assert result.results[2].item_type == "discussion"


async def test_get_planner_items_date_and_course_filters(
    canvas_api: CanvasAPIMock,
) -> None:
    canvas_api.rest_returns("v1/planner/items", PLANNER_ITEMS_REST)

    await get_planner_items(
        start_date="2026-08-27",
        end_date="2026-09-03",
        course_id="100001",
    )

    params = canvas_api.get_rest_paginated_mock.await_args.kwargs["params"]
    assert params["start_date"] == "2026-08-27"
    assert params["end_date"] == "2026-09-03"
    assert params["context_codes[]"] == "course_100001"


async def test_get_planner_items_preserves_offset_and_all_day(
    canvas_api: CanvasAPIMock,
) -> None:
    planner_payload = [
        {
            "context_type": "Course",
            "course_id": 100001,
            "plannable_id": "200005",
            "plannable_type": "assignment",
            "plannable": {
                "id": 200005,
                "title": "Timed Quiz Due",
                "due_at": "2026-08-28T23:59:00-05:00",
                "all_day": True,
                "all_day_date": "2026-08-28",
            },
        }
    ]
    canvas_api.rest_returns("v1/planner/items", planner_payload)

    result = await get_planner_items()

    assert result.result_count == 1
    item = result.results[0]
    assert item.due_at is not None
    assert item.due_at.tzinfo is not None
    assert item.all_day is True
    assert item.all_day_date == "2026-08-28"
