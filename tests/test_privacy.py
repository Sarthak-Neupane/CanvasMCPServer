"""
Privacy regression suite (extends P0.5).

Run with: uv run pytest -m privacy
"""

from __future__ import annotations

import pytest

from canvas_mcp_server.tools.grades.get_course_grades import get_course_grades
from canvas_mcp_server.tools.submissions.get_submission_status import (
    get_submission_status,
)
from tests.fixtures.grades import (
    COURSE_GRADES_ALL_STUDENTS_GRAPHQL,
    COURSE_GRADES_GRAPHQL,
    COURSE_GRADES_ROSTER_LEAK_GRAPHQL,
    COURSE_GRADES_TEACHER_SCOPED_GRAPHQL,
    USERS_SELF_REST,
)
from tests.fixtures.submissions import (
    SUBMISSION_STATUS_GRAPHQL,
    SUBMISSION_STATUS_ROSTER_LEAK_GRAPHQL,
)
from tests.helpers.canvas_mock import CanvasAPIMock

pytestmark = pytest.mark.privacy


async def test_privacy_submission_status_never_returns_classmates(
    canvas_api: CanvasAPIMock,
) -> None:
    canvas_api.rest_returns("v1/users/self", USERS_SELF_REST)
    canvas_api.graphql_returns(SUBMISSION_STATUS_ROSTER_LEAK_GRAPHQL)

    result = await get_submission_status("200001")

    assert len(result.submissions) == 1
    assert result.submissions[0].user is not None
    assert result.submissions[0].user.id == "700001"


async def test_privacy_course_grades_student_never_returns_classmate_roster(
    canvas_api: CanvasAPIMock,
) -> None:
    canvas_api.rest_returns("v1/users/self", USERS_SELF_REST)
    canvas_api.graphql_returns(COURSE_GRADES_ROSTER_LEAK_GRAPHQL)

    result = await get_course_grades("100001")

    assert len(result.enrollments) == 1
    assert result.enrollments[0].user is not None
    assert result.enrollments[0].user.id == "700001"


async def test_privacy_course_grades_student_scoped_query_uses_self_id(
    canvas_api: CanvasAPIMock,
) -> None:
    canvas_api.rest_returns("v1/users/self", USERS_SELF_REST)
    canvas_api.graphql_returns(COURSE_GRADES_GRAPHQL)

    await get_course_grades("100001")

    variables = canvas_api.graphql.await_args.kwargs["variables"]
    assert variables["userIds"] == ["700001"]


async def test_privacy_submission_status_student_scope(
    canvas_api: CanvasAPIMock,
) -> None:
    canvas_api.rest_returns("v1/users/self", USERS_SELF_REST)
    canvas_api.graphql_returns(SUBMISSION_STATUS_GRAPHQL)

    result = await get_submission_status("200001")

    assert len(result.submissions) == 1
    assert result.submissions[0].user is not None
    assert result.submissions[0].user.id == "700001"


async def test_privacy_course_grades_first_query_always_student_scoped(
    canvas_api: CanvasAPIMock,
) -> None:
    """Even when grade-view permission exists, the first GraphQL call is self-scoped."""
    canvas_api.rest_returns("v1/users/self", USERS_SELF_REST)
    canvas_api.graphql_returns(COURSE_GRADES_TEACHER_SCOPED_GRAPHQL)
    canvas_api.graphql_returns(COURSE_GRADES_ALL_STUDENTS_GRAPHQL)

    await get_course_grades("100001")

    first_call = canvas_api.graphql.await_args_list[0]
    variables = first_call.kwargs["variables"]
    assert variables["userIds"] == ["700001"]
