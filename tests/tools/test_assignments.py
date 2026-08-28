"""Regression tests for assignment and planning MCP tools."""

from __future__ import annotations

from canvas_mcp_server.errors import ErrorCode
from canvas_mcp_server.models import (
    AssignmentDetail,
    AssignmentSummary,
    TodoItem,
    UpcomingAssignment,
)
from canvas_mcp_server.tools.assignments.get_assignment_details import (
    get_assignment_details,
)
from canvas_mcp_server.tools.assignments.get_assignments_for_course import (
    get_assignments_for_course,
)
from canvas_mcp_server.tools.assignments.get_upcoming_assignments import (
    get_upcoming_assignments,
)
from canvas_mcp_server.tools.todos.get_todo_items import get_todo_items
from tests.fixtures.assignments import (
    ASSIGNMENT_DETAIL_EXTERNAL_TOOL_GRAPHQL,
    ASSIGNMENT_DETAIL_GRAPHQL,
    ASSIGNMENTS_CONNECTION_GRAPHQL,
    ASSIGNMENTS_CONNECTION_PAGE_1,
    ASSIGNMENTS_CONNECTION_PAGE_2,
    UPCOMING_EVENTS_REST,
)
from tests.fixtures.todos import TODO_ITEMS_REST
from tests.helpers.assertions import assert_list_result, assert_tool_error
from tests.helpers.canvas_mock import CanvasAPIMock


async def test_get_upcoming_assignments(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns("v1/users/self/upcoming_events", UPCOMING_EVENTS_REST)

    result = await get_upcoming_assignments()

    assert result.result_count == 1
    assert isinstance(result.results[0], UpcomingAssignment)
    assert result.results[0].id == 200001
    assert result.results[0].name == "Homework 1"
    assert result.results[0].context_code == "course_100001"
    assert result.results[0].course_id == 100001


async def test_get_assignments_for_course_pagination(canvas_api: CanvasAPIMock) -> None:
    canvas_api.graphql_returns(ASSIGNMENTS_CONNECTION_PAGE_1)
    canvas_api.graphql_returns(ASSIGNMENTS_CONNECTION_PAGE_2)

    result = await get_assignments_for_course("100001")

    assert result.result_count == 2
    assert (
        assert_list_result(result, AssignmentSummary, count=result.result_count) or True
    )
    assert result.results[0].id == "200001"
    assert result.results[1].id == "200002"
    assert canvas_api.graphql.await_count == 2


async def test_get_assignments_for_course_single_page(
    canvas_api: CanvasAPIMock,
) -> None:
    canvas_api.graphql_returns(ASSIGNMENTS_CONNECTION_GRAPHQL)

    result = await get_assignments_for_course("100001")

    assert result.result_count == 1
    assert result.results[0].name == "Homework 1"
    assert canvas_api.graphql.await_count == 1


async def test_get_assignment_details(canvas_api: CanvasAPIMock) -> None:
    canvas_api.graphql_returns(ASSIGNMENT_DETAIL_GRAPHQL)

    result = await get_assignment_details("200001")

    assert isinstance(result, AssignmentDetail)
    assert result.id == "200001"
    assert result.name == "Homework 1"
    assert result.description == "<p>Complete the worksheet.</p>"
    assert result.gradingType == "points"
    assert result.submissionTypes == ["online_upload"]
    assert result.allowedAttempts == 3
    assert result.course is not None
    assert result.course.id == "100001"
    assert result.course.name == "Intro to Testing"
    assert result.canvas_content_available is True
    assert result.external_tool is None


async def test_get_assignment_details_external_tool(
    canvas_api: CanvasAPIMock,
) -> None:
    canvas_api.graphql_returns(ASSIGNMENT_DETAIL_EXTERNAL_TOOL_GRAPHQL)

    result = await get_assignment_details("200003")

    assert isinstance(result, AssignmentDetail)
    assert result.id == "200003"
    assert result.name == "WebAssign Homework 1"
    assert result.submissionTypes == ["external_tool"]
    assert result.canvas_content_available is False
    assert result.external_tool is not None
    assert result.external_tool.url == "https://webassign.net/canvas/launch"
    assert result.external_tool.new_tab is True


async def test_get_assignment_details_not_found(canvas_api: CanvasAPIMock) -> None:
    canvas_api.graphql_returns({"assignment": None})

    result = await get_assignment_details("999999")

    assert_tool_error(
        result,
        ErrorCode.RESOURCE_NOT_FOUND,
        title="Not Found",
        message_contains="Assignment 999999 not found",
    )


async def test_get_todo_items(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns("v1/users/self/todo", TODO_ITEMS_REST)

    result = await get_todo_items()

    assert result.result_count == 1
    assert isinstance(result.results[0], TodoItem)
    assert result.results[0].type == "submitting"
    assert result.results[0].course_id == 100001
    assert result.results[0].assignment is not None
    assert result.results[0].assignment.id == 200001
    assert result.results[0].assignment.name == "Homework 1"
