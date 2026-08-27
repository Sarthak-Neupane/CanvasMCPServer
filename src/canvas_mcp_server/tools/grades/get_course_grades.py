"""Tool for fetching grades in a Canvas course via the GraphQL API."""

from typing import Final, Dict, Any, List, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import CourseGrades, EnrollmentGrade
from ...errors import as_tool_error
from ..submissions._user import current_user_id
from ...utils import canvas_api_client, extract_graphql_data
from ...utils.graphql_pagination import (
    DEFAULT_GRAPHQL_MAX_PAGES,
    DEFAULT_GRAPHQL_PAGE_SIZE,
    paginate_graphql_connection,
)

CourseGradesResponse: TypeAlias = Union[CourseGrades, Dict[str, Any]]

# Do NOT rely on Canvas auto-scoping enrollmentsConnection for students.
# Live student tokens can still receive the full course roster (classmate
# names) when userIds is omitted; grade fields for others are usually null,
# but returning the roster is itself a data-authorization leak. Always check
# viewAllGrades/manageGrades and, when absent, request only the current user.
GRADES_QUERY = """
query ($courseId: ID!, $userIds: [ID!]) {
  course(id: $courseId) {
    _id
    name
    permissions {
      viewAllGrades
      manageGrades
    }
    enrollmentsConnection(filter: {types: [StudentEnrollment], userIds: $userIds}) {
      nodes {
        _id
        type
        user {
          _id
          name
        }
        grades {
          currentScore
          currentGrade
          finalScore
          finalGrade
        }
      }
    }
  }
}
"""

ALL_STUDENT_GRADES_QUERY = """
query ($courseId: ID!, $first: Int!, $after: String) {
  course(id: $courseId) {
    _id
    name
    enrollmentsConnection(
      first: $first
      after: $after
      filter: {types: [StudentEnrollment]}
    ) {
      nodes {
        _id
        type
        user {
          _id
          name
        }
        grades {
          currentScore
          currentGrade
          finalScore
          finalGrade
        }
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}
"""


async def _fetch_all_student_enrollments(course_id: str) -> List[Dict[str, Any]]:
    async def fetch_connection(after: str | None) -> Dict[str, Any]:
        response = await canvas_api_client.post_graphql_query(
            query=ALL_STUDENT_GRADES_QUERY,
            variables={
                "courseId": course_id,
                "first": DEFAULT_GRAPHQL_PAGE_SIZE,
                "after": after,
            },
        )
        data = extract_graphql_data(response)
        course = data.get("course")
        if course is None:
            raise Exception(f"No course found for id: {course_id}")
        return course.get("enrollmentsConnection") or {"nodes": []}

    return await paginate_graphql_connection(
        fetch_connection,
        max_pages=DEFAULT_GRAPHQL_MAX_PAGES,
    )


def _enrollment_nodes(course: Dict[str, Any]) -> List[Dict[str, Any]]:
    connection = course.get("enrollmentsConnection") or {"nodes": []}
    nodes = connection.get("nodes") or []
    return [node for node in nodes if isinstance(node, dict)]


async def get_course_grades(
    course_id: Annotated[
        str,
        Field(
            description=(
                "The course ID. Accepts either the numeric Canvas ID "
                "(e.g. '123456') or the GraphQL global ID."
            ),
        ),
    ],
) -> CourseGradesResponse:
    """
    Get grades for a Canvas course.

    Returns current and final scores/grades for the current grading period.
    Students see only their own enrollment; teachers/TAs with grade-view
    permission see all students. Roster visibility is enforced in this tool —
    Canvas GraphQL does not reliably auto-scope enrollmentsConnection for
    students.

    Returns an error object with "error", "message", and optionally
    "status_code" keys on failure.
    """
    try:
        self_id = await current_user_id()

        # Always start scoped to self so a student token never pulls the roster.
        scoped_response = await canvas_api_client.post_graphql_query(
            query=GRADES_QUERY,
            variables={"courseId": course_id, "userIds": [self_id]},
        )
        scoped_data = extract_graphql_data(scoped_response)
        course = scoped_data.get("course")
        if course is None:
            raise Exception(f"No course found for id: {course_id}")

        permissions = course.get("permissions") or {}
        can_view_all = bool(
            permissions.get("viewAllGrades") or permissions.get("manageGrades")
        )

        if can_view_all:
            paginated = await _fetch_all_student_enrollments(course_id)
            nodes = paginated.items
        else:
            nodes = _enrollment_nodes(course)
            # Defense in depth: never return another user's enrollment to a
            # caller without grade-view permission, even if Canvas expands the
            # connection unexpectedly.
            nodes = [
                node
                for node in nodes
                if str((node.get("user") or {}).get("_id")) == self_id
            ]

        enrollments = [EnrollmentGrade.model_validate(node) for node in nodes]
        return CourseGrades(
            courseId=course["_id"],
            courseName=course.get("name"),
            enrollments=enrollments,
            result_count=len(enrollments),
        )

    except Exception as e:
        return as_tool_error(e, source="canvas_graphql")


get_course_grades_tool: Final[Tool] = Tool.from_function(
    name="get_course_grades",
    description=(
        "Get grades for a Canvas course: current and final scores/grades. "
        "Students see only their own enrollment; teachers with grade "
        "permission see all students. Classmate rosters are never returned "
        "to student callers."
    ),
    fn=get_course_grades,
)
