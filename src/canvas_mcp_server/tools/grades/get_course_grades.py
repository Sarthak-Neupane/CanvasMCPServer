"""Tool for fetching grades in a Canvas course via the GraphQL API."""

from typing import Final, Dict, Any, List, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import CourseGrades, EnrollmentGrade
from ...utils import canvas_api_client, extract_graphql_data, HTTPError

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
query ($courseId: ID!) {
  course(id: $courseId) {
    _id
    name
    enrollmentsConnection(filter: {types: [StudentEnrollment]}) {
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


async def _current_user_id() -> str:
    """Resolve the authenticated Canvas user's numeric id."""
    response = await canvas_api_client.get_rest("v1/users/self")
    data = response.data
    if not isinstance(data, dict) or data.get("id") is None:
        raise Exception("Could not resolve the current Canvas user id")
    return str(data["id"])


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
        self_id = await _current_user_id()

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
            all_response = await canvas_api_client.post_graphql_query(
                query=ALL_STUDENT_GRADES_QUERY,
                variables={"courseId": course_id},
            )
            all_data = extract_graphql_data(all_response)
            course = all_data.get("course") or course
            nodes = _enrollment_nodes(course)
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
        )

    except HTTPError as e:
        return {
            "error": "HTTP Error",
            "message": str(e),
            "status_code": e.status_code,
        }
    except Exception as e:
        return {
            "error": "Unexpected Error",
            "message": str(e),
        }


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
