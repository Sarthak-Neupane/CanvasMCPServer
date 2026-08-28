"""Regression tests for discussion MCP tools."""

from canvas_mcp_server.errors import ErrorCode, tool_error_from_http
from canvas_mcp_server.models import (
    DiscussionDetail,
    DiscussionEntries,
    DiscussionSummary,
)
from canvas_mcp_server.tools.discussions.get_course_discussions import (
    get_course_discussions,
)
from canvas_mcp_server.tools.discussions.get_discussion import get_discussion
from canvas_mcp_server.tools.discussions.get_discussion_entries import (
    get_discussion_entries,
)
from canvas_mcp_server.utils.http_client import HTTPError
from tests.fixtures.discussions import (
    DISCUSSION_DETAIL_REST,
    DISCUSSION_VIEW_REST,
    DISCUSSIONS_LIST_REST,
)
from tests.helpers.assertions import (
    assert_http_error,
    assert_list_result,
    assert_tool_error,
)
from tests.helpers.canvas_mock import CanvasAPIMock


def test_discussion_http_error_require_initial_post() -> None:
    error = HTTPError(
        "HTTP 403 error: require_initial_post",
        status_code=403,
        response_data="require_initial_post",
    )
    result = tool_error_from_http(error, source="canvas_rest").to_response()
    assert_tool_error(
        result,
        ErrorCode.DISCUSSION_LOCKED,
        status_code=403,
        title="Discussion Locked",
    )
    assert result["lock_reason"] == "require_initial_post"


async def test_get_course_discussions_success(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns(
        "v1/courses/100001/discussion_topics",
        DISCUSSIONS_LIST_REST,
    )

    result = await get_course_discussions("100001")

    assert result.result_count == 2
    assert (
        assert_list_result(result, DiscussionSummary, count=result.result_count) or True
    )
    assert result.results[0].discussion_id == 400001
    assert result.results[0].require_initial_post is True
    assert result.results[1].locked_for_user is True
    assert result.results[1].lock_explanation is not None


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


async def test_get_course_discussions_filters_out_announcements(
    canvas_api: CanvasAPIMock,
) -> None:
    mixed_payload = [
        {
            "id": 400001,
            "title": "Regular Discussion",
            "is_announcement": False,
        },
        {
            "id": 400002,
            "title": "Course Announcement",
            "is_announcement": True,
        },
        {
            "id": 400003,
            "title": "Another Announcement",
            "announcement": True,
        },
        {
            "id": 400004,
            "title": "Genuine Discussion",
            "is_announcement": False,
        },
    ]
    canvas_api.rest_returns(
        "v1/courses/100001/discussion_topics",
        mixed_payload,
    )

    result = await get_course_discussions("100001")

    assert result.result_count == 2
    assert [d.discussion_id for d in result.results] == [400001, 400004]
    assert [d.title for d in result.results] == [
        "Regular Discussion",
        "Genuine Discussion",
    ]


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
    assert result.source_type == "discussion"
    assert result.course_id == "100001"
    assert result.canvas_url is not None
    assert result.canvas_url.endswith("/courses/100001/discussion_topics/400001")


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
    assert result.entries[0].source_type == "discussion_entry"
    assert result.entries[0].course_id == "100001"
    assert result.entries[0].canvas_url == (
        "/courses/100001/discussion_topics/400001/entries/11"
    )


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

    canvas_api._rest_routes["v1/courses/100001/discussion_topics/400001/view"] = _raise

    result = await get_discussion_entries("100001", "400001")

    assert_tool_error(
        result,
        ErrorCode.DISCUSSION_LOCKED,
        status_code=403,
        title="Discussion Locked",
    )
    assert result["lock_reason"] == "require_initial_post"


async def test_get_discussion_http_error(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_error(
        "v1/courses/100001/discussion_topics/400001",
        status_code=404,
        message="Not found",
    )

    result = await get_discussion("100001", "400001")

    assert_http_error(result, 404)
