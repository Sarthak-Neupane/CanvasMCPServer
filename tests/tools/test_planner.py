"""Regression tests for planner tools."""

from canvas_mcp_server.models import PlannerItem
from canvas_mcp_server.tools.planner._parse import normalize_plannable_type
from canvas_mcp_server.tools.planner.get_planner_items import get_planner_items
from tests.fixtures.planner import PLANNER_ITEMS_REST
from tests.helpers.canvas_mock import CanvasAPIMock


def test_normalize_plannable_type() -> None:
    assert normalize_plannable_type("discussion_topic") == "discussion"
    assert normalize_plannable_type("wiki_page") == "page"
    assert normalize_plannable_type("planner_note") == "note"


async def test_get_planner_items_success(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns("v1/planner/items", PLANNER_ITEMS_REST)

    result = await get_planner_items()

    assert isinstance(result, list)
    assert len(result) == 3
    assert all(isinstance(item, PlannerItem) for item in result)
    assert result[0].item_type == "assignment"
    assert result[0].title == "Homework 1"
    assert result[0].submissions is not None
    assert result[0].submissions.missing is True
    assert result[1].item_type == "note"
    assert result[2].item_type == "discussion"


async def test_get_planner_items_date_and_course_filters(
    canvas_api: CanvasAPIMock,
) -> None:
    canvas_api.rest_returns("v1/planner/items", PLANNER_ITEMS_REST)

    await get_planner_items(
        start_date="2026-08-27",
        end_date="2026-09-03",
        course_id="100001",
    )

    params = canvas_api.rest.await_args.kwargs["params"]
    assert params["start_date"] == "2026-08-27"
    assert params["end_date"] == "2026-09-03"
    assert params["context_codes[]"] == "course_100001"
