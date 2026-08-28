"""Regression tests for wiki page MCP tools."""

from __future__ import annotations

import pytest

from canvas_mcp_server.models import (
    AssignmentResourceType,
    PageDetail,
    PageResources,
    PageSummary,
)
from canvas_mcp_server.tools.pages._params import (
    normalize_page_locator,
    page_endpoint_segment,
)
from canvas_mcp_server.tools.pages.get_course_pages import get_course_pages
from canvas_mcp_server.tools.pages.get_page import get_page
from canvas_mcp_server.tools.pages.get_page_resources import get_page_resources
from tests.fixtures.pages import (
    PAGE_DETAIL_EMPTY_RESOURCES_REST,
    PAGE_DETAIL_REST,
    PAGE_DETAIL_WITH_RESOURCES_REST,
    PAGES_LIST_REST,
)
from tests.helpers.assertions import assert_http_error, assert_list_result
from tests.helpers.canvas_mock import CanvasAPIMock


def test_normalize_page_locator() -> None:
    assert normalize_page_locator("week-1-overview") == "week-1-overview"
    assert (
        normalize_page_locator("/courses/100001/pages/week-1-overview")
        == "week-1-overview"
    )


def test_page_endpoint_segment_uses_page_id_prefix_for_numeric_ids() -> None:
    assert page_endpoint_segment("700001") == "page_id:700001"
    assert page_endpoint_segment("week-1-overview") == "week-1-overview"


async def test_get_course_pages_success(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns("v1/courses/100001/pages", PAGES_LIST_REST)

    result = await get_course_pages("100001")

    assert result.result_count == 2
    assert all(isinstance(page, PageSummary) for page in result.results)
    assert result.results[0].url == "week-1-overview"
    assert result.results[1].front_page is True


async def test_get_course_pages_search_term(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns("v1/courses/100001/pages", PAGES_LIST_REST)

    await get_course_pages("100001", search_term="Week 1")

    assert canvas_api.get_rest_paginated_mock.await_args is not None
    assert (
        canvas_api.get_rest_paginated_mock.await_args.kwargs["params"]["search_term"]
        == "Week 1"
    )


async def test_get_page_by_slug(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns(
        "v1/courses/100001/pages/week-1-overview",
        PAGE_DETAIL_REST,
    )

    result = await get_page("100001", "week-1-overview")

    assert isinstance(result, PageDetail)
    assert result.page_id == 700001
    assert result.title == "Week 1 Overview"
    assert result.body is not None
    assert result.body_text is not None
    assert "Week 1" in result.body_text
    assert "Read chapter 1." in result.body_text
    assert "bad()" not in result.body_text
    assert result.source_type == "page"
    assert result.course_id == "100001"
    assert result.canvas_url == "/courses/100001/pages/week-1-overview"


async def test_get_page_by_full_canvas_path(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns(
        "v1/courses/100001/pages/week-1-overview",
        PAGE_DETAIL_REST,
    )

    result = await get_page("100001", "/courses/100001/pages/week-1-overview")

    assert isinstance(result, PageDetail)
    assert result.url == "week-1-overview"


async def test_get_page_by_numeric_id(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns(
        "v1/courses/100001/pages/page_id:700001",
        PAGE_DETAIL_REST,
    )

    result = await get_page("100001", "700001")

    assert isinstance(result, PageDetail)
    assert result.page_id == 700001


async def test_get_page_not_found(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_error(
        "v1/courses/100001/pages/missing-page",
        status_code=404,
        message="Canvas API endpoint not found",
    )

    result = await get_page("100001", "missing-page")

    assert_http_error(result, 404)


async def test_get_page_resources_success(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns(
        "v1/courses/100001/pages/lecture-2-materials",
        PAGE_DETAIL_WITH_RESOURCES_REST,
    )

    result = await get_page_resources("100001", "lecture-2-materials")

    assert isinstance(result, PageResources)
    assert result.course_id == "100001"
    assert result.page_url == "lecture-2-materials"
    assert result.page_title == "Lecture 2 Materials"
    assert result.status == "ok"
    assert result.result_count == 3
    assert len(result.resources) == 3

    file_res = next(
        r for r in result.resources if r.type == AssignmentResourceType.FILE
    )
    assert file_res.id == "500002"
    assert file_res.label == "Lecture Slides"

    page_res = next(
        r for r in result.resources if r.type == AssignmentResourceType.PAGE
    )
    assert page_res.id == "week-1-overview"

    ext_res = next(
        r for r in result.resources if r.type == AssignmentResourceType.EXTERNAL_URL
    )
    assert ext_res.url == "https://example.com/reading"


async def test_get_page_resources_empty(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns(
        "v1/courses/100001/pages/announcements-summary",
        PAGE_DETAIL_EMPTY_RESOURCES_REST,
    )

    result = await get_page_resources("100001", "announcements-summary")

    assert isinstance(result, PageResources)
    assert result.status == "empty"
    assert result.result_count == 0
    assert result.resources == []
    assert result.empty_reason is not None


async def test_get_page_resources_not_found(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_error(
        "v1/courses/100001/pages/missing-page",
        status_code=404,
        message="Canvas API endpoint not found",
    )

    result = await get_page_resources("100001", "missing-page")

    assert_http_error(result, 404)
