"""Regression tests for assignment and planning MCP tools."""

from __future__ import annotations

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
    ASSIGNMENT_DETAIL_GRAPHQL,
    ASSIGNMENTS_CONNECTION_GRAPHQL,
    ASSIGNMENTS_CONNECTION_PAGE_1,
    ASSIGNMENTS_CONNECTION_PAGE_2,
    UPCOMING_EVENTS_REST,
)
from tests.fixtures.todos import TODO_ITEMS_REST
from tests.helpers.canvas_mock import CanvasAPIMock


async def test_get_upcoming_assignments(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns("v1/users/self/upcoming_events", UPCOMING_EVENTS_REST)

    result = await get_upcoming_assignments()

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], UpcomingAssignment)
    assert result[0].id == 200001
    assert result[0].name == "Homework 1"
    assert result[0].context_code == "course_100001"
    assert result[0].course_id == 100001


async def test_get_assignments_for_course_pagination(canvas_api: CanvasAPIMock) -> None:
    canvas_api.graphql_returns(ASSIGNMENTS_CONNECTION_PAGE_1)
    canvas_api.graphql_returns(ASSIGNMENTS_CONNECTION_PAGE_2)

    result = await get_assignments_for_course("100001")

    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(item, AssignmentSummary) for item in result)
    assert result[0].id == "200001"
    assert result[1].id == "200002"
    assert canvas_api.graphql.await_count == 2


async def test_get_assignments_for_course_single_page(canvas_api: CanvasAPIMock) -> None:
    canvas_api.graphql_returns(ASSIGNMENTS_CONNECTION_GRAPHQL)

    result = await get_assignments_for_course("100001")

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].name == "Homework 1"
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


async def test_get_todo_items(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns("v1/users/self/todo", TODO_ITEMS_REST)

    result = await get_todo_items()

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TodoItem)
    assert result[0].type == "submitting"
    assert result[0].course_id == 100001
    assert result[0].assignment is not None
    assert result[0].assignment.id == 200001
    assert result[0].assignment.name == "Homework 1"
