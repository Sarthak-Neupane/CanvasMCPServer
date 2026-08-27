"""Regression tests for module MCP tools."""

from __future__ import annotations

from canvas_mcp_server.models import ModuleItemDetail, ModuleItemSummary, ModuleSummary
from canvas_mcp_server.tools.modules.get_course_modules import get_course_modules
from canvas_mcp_server.tools.modules.get_module_item_details import get_module_item_details
from canvas_mcp_server.tools.modules.get_module_items import get_module_items
from tests.fixtures.modules import (
    MODULE_ITEM_DETAIL_REST,
    MODULE_ITEMS_REST,
    MODULES_LIST_REST,
)
from tests.helpers.canvas_mock import CanvasAPIMock


async def test_get_course_modules_structure_only(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns("v1/courses/100001/modules", MODULES_LIST_REST)

    result = await get_course_modules("100001")

    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(module, ModuleSummary) for module in result)
    assert result[0].name == "Week 1"
    assert result[0].items_count == 3
    assert result[1].state == "locked"
    assert not hasattr(result[0], "items")

    call = canvas_api.rest.await_args
    assert call is not None
    params = call.kwargs["params"]
    assert "include[]" not in params
    assert params["per_page"] == 100


async def test_get_module_items(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns(
        "v1/courses/100001/modules/300001/items",
        MODULE_ITEMS_REST,
    )

    result = await get_module_items("100001", "300001")

    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(item, ModuleItemSummary) for item in result)
    assert result[0].type == "File"
    assert result[0].content_id == 500001
    assert result[1].type == "Page"
    assert result[1].page_url == "chapter-1"


async def test_get_module_item_details_with_content_details(
    canvas_api: CanvasAPIMock,
) -> None:
    canvas_api.rest_returns(
        "v1/courses/100001/modules/300001/items/400001",
        MODULE_ITEM_DETAIL_REST,
    )

    result = await get_module_item_details("100001", "300001", "400001")

    assert isinstance(result, ModuleItemDetail)
    assert result.id == 400001
    assert result.type == "Assignment"
    assert result.content_details is not None
    assert result.content_details.points_possible == 10.0
    assert result.content_details.due_at is not None
    assert result.content_details.locked_for_user is False
    assert result.completion_requirement is not None
    assert result.completion_requirement.type == "must_submit"

    call = canvas_api.rest.await_args
    assert call is not None
    assert call.kwargs["params"]["include[]"] == "content_details"
