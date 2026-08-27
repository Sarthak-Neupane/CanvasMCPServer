"""Regression tests for grades, submissions, and announcements tools."""

from __future__ import annotations

from canvas_mcp_server.models import (
    AnnouncementSummary,
    AssignmentSubmissions,
    CourseGrades,
)
from canvas_mcp_server.tools.announcements.get_announcements import get_announcements
from canvas_mcp_server.tools.grades.get_course_grades import get_course_grades
from canvas_mcp_server.tools.submissions.get_submission_status import (
    get_submission_status,
)
from tests.fixtures.announcements import (
    ANNOUNCEMENTS_GRAPHQL,
    ANNOUNCEMENTS_PAGE_1,
    ANNOUNCEMENTS_PAGE_2,
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
from tests.helpers.assertions import assert_list_result
from tests.helpers.canvas_mock import CanvasAPIMock


async def test_get_submission_status_student_scope(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns("v1/users/self", USERS_SELF_REST)
    canvas_api.graphql_returns(SUBMISSION_STATUS_GRAPHQL)

    result = await get_submission_status("200001")

    assert isinstance(result, AssignmentSubmissions)
    assert result.assignmentId == "200001"
    assert len(result.submissions) == 1
    submission = result.submissions[0]
    assert submission.user is not None
    assert submission.user.id == "700001"
    assert submission.user.name == "Test Student"
    assert submission.score == 9.0
    assert submission.gradingStatus == "graded"

    call = canvas_api.graphql.await_args
    assert call is not None
    assert call.kwargs["variables"]["assignmentId"] == "200001"
    assert call.kwargs["variables"]["first"] == 100


async def test_get_submission_status_filters_roster_leak(
    canvas_api: CanvasAPIMock,
) -> None:
    canvas_api.rest_returns("v1/users/self", USERS_SELF_REST)
    canvas_api.graphql_returns(SUBMISSION_STATUS_ROSTER_LEAK_GRAPHQL)

    result = await get_submission_status("200001")

    assert isinstance(result, AssignmentSubmissions)
    assert len(result.submissions) == 1
    assert result.submissions[0].user is not None
    assert result.submissions[0].user.id == "700001"


async def test_get_course_grades_student_single_enrollment(
    canvas_api: CanvasAPIMock,
) -> None:
    canvas_api.rest_returns("v1/users/self", USERS_SELF_REST)
    canvas_api.graphql_returns(COURSE_GRADES_GRAPHQL)

    result = await get_course_grades("100001")

    assert isinstance(result, CourseGrades)
    assert result.courseId == "100001"
    assert len(result.enrollments) == 1
    assert result.enrollments[0].user is not None
    assert result.enrollments[0].user.id == "700001"
    assert result.enrollments[0].grades is not None
    assert result.enrollments[0].grades.currentScore == 92.5
    assert canvas_api.graphql.await_count == 1

    variables = canvas_api.graphql.await_args.kwargs["variables"]
    assert variables["courseId"] == "100001"
    assert variables["userIds"] == ["700001"]


async def test_get_course_grades_student_filters_roster_leak(
    canvas_api: CanvasAPIMock,
) -> None:
    canvas_api.rest_returns("v1/users/self", USERS_SELF_REST)
    canvas_api.graphql_returns(COURSE_GRADES_ROSTER_LEAK_GRAPHQL)

    result = await get_course_grades("100001")

    assert isinstance(result, CourseGrades)
    assert len(result.enrollments) == 1
    assert result.enrollments[0].user is not None
    assert result.enrollments[0].user.id == "700001"


async def test_get_course_grades_teacher_returns_all_students(
    canvas_api: CanvasAPIMock,
) -> None:
    canvas_api.rest_returns("v1/users/self", USERS_SELF_REST)
    canvas_api.graphql_returns(COURSE_GRADES_TEACHER_SCOPED_GRAPHQL)
    canvas_api.graphql_returns(COURSE_GRADES_ALL_STUDENTS_GRAPHQL)

    result = await get_course_grades("100001")

    assert isinstance(result, CourseGrades)
    assert len(result.enrollments) == 2
    user_ids = {
        enrollment.user.id
        for enrollment in result.enrollments
        if enrollment.user is not None
    }
    assert user_ids == {"700001", "700002"}
    assert canvas_api.graphql.await_count == 2


async def test_get_announcements(canvas_api: CanvasAPIMock) -> None:
    canvas_api.graphql_returns(ANNOUNCEMENTS_GRAPHQL)

    result = await get_announcements("100001")

    assert result.result_count == 1
    assert isinstance(result.results[0], AnnouncementSummary)
    assert result.results[0].id == "110001"
    assert result.results[0].title == "Exam moved to Friday"
    assert result.results[0].author is not None
    assert result.results[0].author.name == "Dr. Instructor"


async def test_get_announcements_pagination(canvas_api: CanvasAPIMock) -> None:
    canvas_api.graphql_returns(ANNOUNCEMENTS_PAGE_1)
    canvas_api.graphql_returns(ANNOUNCEMENTS_PAGE_2)

    result = await get_announcements("100001")

    assert result.result_count == 2
    assert {item.id for item in result.results} == {"110001", "110002"}
    assert canvas_api.graphql.await_count == 2
