"""Tool for fetching grades in a Canvas course via the GraphQL API."""

from typing import Final, Dict, Any, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import CourseGrades, EnrollmentGrade
from ...utils import canvas_api_client, extract_graphql_data, HTTPError

CourseGradesResponse: TypeAlias = Union[CourseGrades, Dict[str, Any]]

# Enrollment visibility is scoped server-side: students get their own
# enrollment, teachers get every student in the course.
GRAPHQL_QUERY = """
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
    Students see their own grades; teachers see grades for all students.
    Returns an error object with "error", "message", and optionally
    "status_code" keys on failure.
    """
    try:
        response = await canvas_api_client.post_graphql_query(
            query=GRAPHQL_QUERY, variables={"courseId": course_id}
        )
        data = extract_graphql_data(response)
        course = data.get("course")
        if course is None:
            raise Exception(f"No course found for id: {course_id}")

        connection = course.get("enrollmentsConnection") or {"nodes": []}
        enrollments = [
            EnrollmentGrade.model_validate(node) for node in connection["nodes"]
        ]
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
        "Students see their own grades; teachers see all students."
    ),
    fn=get_course_grades,
)
