"""Regression tests for wiki page MCP tools."""

from __future__ import annotations

import pytest

from canvas_mcp_server.models import PageDetail, PageSummary
from canvas_mcp_server.tools.pages._params import (
    normalize_page_locator,
    page_endpoint_segment,
)
from canvas_mcp_server.tools.pages.get_course_pages import get_course_pages
from canvas_mcp_server.tools.pages.get_page import get_page
from tests.fixtures.pages import PAGE_DETAIL_REST, PAGES_LIST_REST
from tests.helpers.assertions import assert_http_error
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

    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(page, PageSummary) for page in result)
    assert result[0].url == "week-1-overview"
    assert result[1].front_page is True


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
