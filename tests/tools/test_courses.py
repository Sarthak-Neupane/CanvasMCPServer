"""Regression tests for course MCP tools."""

from __future__ import annotations

import pytest

from canvas_mcp_server.models import CourseDetail, CourseSummary, CourseSyllabus
from canvas_mcp_server.tools.courses.get_all_courses import get_all_courses
from canvas_mcp_server.tools.courses.get_course_syllabus import get_course_syllabus
from canvas_mcp_server.tools.courses.get_courses_by_id import get_course_by_id
from tests.fixtures.courses import (
    ALL_COURSES_GRAPHQL,
    COURSE_BY_ID_GRAPHQL,
    DASHBOARD_CARDS_REST,
    REST_COURSES_ACTIVE,
    SYLLABUS_EMPTY_REST,
    SYLLABUS_HTML_REST,
)
from tests.helpers.assertions import assert_http_error, assert_list_result
from tests.helpers.canvas_mock import CanvasAPIMock


async def test_get_all_courses_graphql_success(canvas_api: CanvasAPIMock) -> None:
    canvas_api.graphql_returns(ALL_COURSES_GRAPHQL)

    result = await get_all_courses()

    assert result.result_count == 2
    assert all(isinstance(course, CourseSummary) for course in result.results)
    assert result.results[0].name == "Intro to Testing"
    assert result.results[0].courseCode == "TEST101"
    assert result.results[0].term is not None
    assert result.results[0].term.name == "Fall 2025"


async def test_get_all_courses_tolerates_missing_name(
    canvas_api: CanvasAPIMock,
) -> None:
    graphql_data = {
        "allCourses": [
            {
                "id": "course-gid-100001",
                "name": None,
                "courseCode": "SHELL101",
                "term": None,
            },
            {
                "id": "course-gid-100002",
                "name": "Valid Course",
                "courseCode": "VAL201",
                "term": {
                    "id": "term-gid-9001",
                    "_id": "9001",
                    "name": "Fall 2025",
                    "startAt": "2025-08-15T00:00:00Z",
                    "endAt": "2025-12-15T23:59:59Z",
                },
            },
        ]
    }
    canvas_api.graphql_returns(graphql_data)

    result = await get_all_courses()

    assert result.result_count == 2
    assert result.results[0].name is None
    assert result.results[0].courseCode == "SHELL101"
    assert result.results[1].name == "Valid Course"


async def test_get_all_courses_term_filter(canvas_api: CanvasAPIMock) -> None:
    canvas_api.graphql_returns(ALL_COURSES_GRAPHQL)
    canvas_api.rest_returns("v1/courses", [REST_COURSES_ACTIVE[0]])

    result = await get_all_courses(term="Fall 2025")

    assert result.result_count == 1
    assert result.results[0].name == "Intro to Testing"
    assert result.results[0].term is not None
    assert result.results[0].term.name == "Fall 2025"
    paginated_call = canvas_api.get_rest_paginated_mock.await_args
    assert paginated_call is not None
    assert paginated_call.kwargs["params"]["enrollment_term_id"] == "9001"


async def test_get_all_courses_active_only_dashboard_intersection(
    canvas_api: CanvasAPIMock,
) -> None:
    canvas_api.rest_returns("v1/dashboard/dashboard_cards", DASHBOARD_CARDS_REST)
    canvas_api.rest_returns("v1/courses/100001", REST_COURSES_ACTIVE[0])

    result = await get_all_courses(active_only=True)

    assert result.result_count == 1
    assert result.results[0].id == "100001"
    assert result.results[0].name == "Intro to Testing"
    assert result.results[0].term is not None
    assert result.results[0].term.name == "Fall 2025"


async def test_get_course_by_id_success(canvas_api: CanvasAPIMock) -> None:
    canvas_api.graphql_returns(COURSE_BY_ID_GRAPHQL)

    result = await get_course_by_id("100001")

    assert isinstance(result, CourseDetail)
    assert result.id == "course-gid-100001"
    assert result.name == "Intro to Testing"
    assert result.courseCode == "TEST101"
    assert result.state.value == "available"


async def test_get_course_syllabus_success(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns("v1/courses/100001", SYLLABUS_HTML_REST)

    result = await get_course_syllabus("100001")

    assert isinstance(result, CourseSyllabus)
    assert result.course_id == "100001"
    assert result.course_name == "Intro to Testing"
    assert result.syllabus_body == "<p>Welcome to Intro to Testing.</p>"


async def test_get_course_syllabus_empty_body(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns("v1/courses/100001", SYLLABUS_EMPTY_REST)

    result = await get_course_syllabus("100001")

    assert isinstance(result, CourseSyllabus)
    assert result.syllabus_body is None


@pytest.mark.parametrize(
    ("status_code", "message"),
    [
        (401, "Canvas API authentication failed."),
        (403, "Canvas API access forbidden."),
        (404, "Canvas API endpoint not found"),
        (429, "Canvas API rate limit exceeded."),
        (503, "Canvas is temporarily unavailable"),
    ],
)
async def test_get_all_courses_http_error_shapes(
    canvas_api: CanvasAPIMock,
    status_code: int,
    message: str,
) -> None:
    canvas_api.graphql_raises(status_code=status_code, message=message)

    result = await get_all_courses()

    assert_http_error(result, status_code)
    assert message in result["message"]


@pytest.mark.parametrize(
    ("status_code", "message"),
    [
        (401, "Canvas API authentication failed."),
        (403, "Canvas API access forbidden."),
        (404, "Canvas API endpoint not found"),
        (429, "Canvas API rate limit exceeded."),
        (503, "Canvas is temporarily unavailable"),
    ],
)
async def test_get_course_by_id_http_error_shapes(
    canvas_api: CanvasAPIMock,
    status_code: int,
    message: str,
) -> None:
    canvas_api.graphql_raises(status_code=status_code, message=message)

    result = await get_course_by_id("100001")

    assert_http_error(result, status_code)
    assert message in result["message"]


@pytest.mark.parametrize(
    ("status_code", "message"),
    [
        (401, "Canvas API authentication failed."),
        (403, "Canvas API access forbidden."),
        (404, "Canvas API endpoint not found"),
        (429, "Canvas API rate limit exceeded."),
        (503, "Canvas is temporarily unavailable"),
    ],
)
async def test_get_course_syllabus_http_error_shapes(
    canvas_api: CanvasAPIMock,
    status_code: int,
    message: str,
) -> None:
    canvas_api.rest_error(
        "v1/courses/100001",
        status_code=status_code,
        message=message,
    )

    result = await get_course_syllabus("100001")

    assert_http_error(result, status_code)
    assert message in result["message"]
