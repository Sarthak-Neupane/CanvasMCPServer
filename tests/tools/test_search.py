"""Regression tests for course content search."""

from canvas_mcp_server.models import SearchResult
from canvas_mcp_server.tools.search._rank import score_document
from canvas_mcp_server.tools.search._snippet import make_snippet
from canvas_mcp_server.tools.search.search_course_content import search_course_content
from tests.fixtures.search import (
    ASSIGNMENTS_SEARCH_GRAPHQL,
    PAGES_SEARCH_REST,
    SYLLABUS_SEARCH_REST,
)
from tests.helpers.canvas_mock import CanvasAPIMock


def test_score_document_exact_title() -> None:
    assert score_document("quiz", "Quiz 1", "") > score_document("quiz", "Homework", "")


def test_make_snippet_bounds_length() -> None:
    text = "alpha " * 100 + "midterm " + "beta " * 100
    snippet = make_snippet(text, "midterm")
    assert "midterm" in snippet.lower()
    assert len(snippet) <= 203


async def test_search_course_content_pages_and_syllabus(
    canvas_api: CanvasAPIMock,
) -> None:
    canvas_api.rest_returns("v1/courses/100001", SYLLABUS_SEARCH_REST)
    canvas_api.rest_returns("v1/courses/100001/pages", PAGES_SEARCH_REST)
    canvas_api.graphql_returns(ASSIGNMENTS_SEARCH_GRAPHQL)

    result = await search_course_content(
        "100001",
        "midterm",
        content_types=["syllabus", "page", "assignment"],
        limit=5,
    )

    assert isinstance(result, list)
    assert len(result) >= 2
    assert all(isinstance(item, SearchResult) for item in result)
    types = {item.content_type for item in result}
    assert "page" in types
    assert result[0].score >= result[-1].score
    assert all(item.snippet is not None for item in result)


async def test_search_course_content_invalid_type(canvas_api: CanvasAPIMock) -> None:
    result = await search_course_content(
        "100001",
        "quiz",
        content_types=["invalid"],
    )

    assert isinstance(result, dict)
    assert result["error"] == "Invalid Request"
