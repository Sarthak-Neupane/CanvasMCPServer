"""Regression tests for discussion MCP tools."""

from canvas_mcp_server.models import (
    DiscussionDetail,
    DiscussionEntries,
    DiscussionSummary,
)
from canvas_mcp_server.tools.discussions._errors import discussion_http_error
from canvas_mcp_server.tools.discussions.get_course_discussions import (
    get_course_discussions,
)
from canvas_mcp_server.tools.discussions.get_discussion import get_discussion
from canvas_mcp_server.tools.discussions.get_discussion_entries import (
    get_discussion_entries,
)
from tests.fixtures.discussions import (
    DISCUSSION_DETAIL_REST,
    DISCUSSION_VIEW_REST,
    DISCUSSIONS_LIST_REST,
)
from tests.helpers.assertions import assert_http_error
from tests.helpers.canvas_mock import CanvasAPIMock
from canvas_mcp_server.utils.http_client import HTTPError


def test_discussion_http_error_require_initial_post() -> None:
    error = HTTPError(
        "HTTP 403 error: require_initial_post",
        status_code=403,
        response_data="require_initial_post",
    )
    result = discussion_http_error(error)
    assert result is not None
    assert result["error"] == "Discussion Locked"
    assert result["lock_reason"] == "require_initial_post"
    assert result["status_code"] == 403


async def test_get_course_discussions_success(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns(
        "v1/courses/100001/discussion_topics",
        DISCUSSIONS_LIST_REST,
    )

    result = await get_course_discussions("100001")

    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(item, DiscussionSummary) for item in result)
    assert result[0].discussion_id == 400001
    assert result[0].require_initial_post is True
    assert result[1].locked_for_user is True
    assert result[1].lock_explanation is not None


async def test_get_course_discussions_search_term(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns(
        "v1/courses/100001/discussion_topics",
        DISCUSSIONS_LIST_REST,
    )

    await get_course_discussions("100001", search_term="Week 1")

    assert canvas_api.get_rest_paginated_mock.await_args is not None
    params = canvas_api.get_rest_paginated_mock.await_args.kwargs["params"]
    assert params["search_term"] == "Week 1"
    assert params["only_announcements"] is False


async def test_get_discussion_success(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns(
        "v1/courses/100001/discussion_topics/400001",
        DISCUSSION_DETAIL_REST,
    )

    result = await get_discussion("100001", "400001")

    assert isinstance(result, DiscussionDetail)
    assert result.title == "Week 1 discussion"
    assert result.message_text == "Introduce yourself."
    assert result.require_initial_post is True


async def test_get_discussion_entries_success(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns(
        "v1/courses/100001/discussion_topics/400001/view",
        DISCUSSION_VIEW_REST,
    )

    result = await get_discussion_entries("100001", "400001")

    assert isinstance(result, DiscussionEntries)
    assert len(result.entries) == 1
    assert result.entries[0].author_name == "Student One"
    assert result.entries[0].message_text == "Hello everyone!"
    assert len(result.entries[0].replies) == 1
    assert result.entries[0].replies[0].author_name == "Student Two"
    assert result.unread_entry_ids == [12]


async def test_get_discussion_entries_require_initial_post(
    canvas_api: CanvasAPIMock,
) -> None:
    async def _raise(*_args, **_kwargs):
        raise HTTPError(
            "HTTP 403 error: require_initial_post",
            status_code=403,
            response_data="require_initial_post",
            url="https://canvas.example.edu/api/v1/courses/100001/discussion_topics/400001/view",
        )

    canvas_api._rest_routes[
        "v1/courses/100001/discussion_topics/400001/view"
    ] = _raise

    result = await get_discussion_entries("100001", "400001")

    assert result["error"] == "Discussion Locked"
    assert result["lock_reason"] == "require_initial_post"
    assert result["status_code"] == 403


async def test_get_discussion_http_error(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_error(
        "v1/courses/100001/discussion_topics/400001",
        status_code=404,
        message="Not found",
    )

    result = await get_discussion("100001", "400001")

    assert_http_error(result, 404)
