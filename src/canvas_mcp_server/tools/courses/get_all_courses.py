"""Tool for listing all Canvas courses via the GraphQL API."""

from typing import Final, List, Dict, Any, Optional, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import CourseSummary
from ...utils import canvas_api_client, HTTPError

CoursesResponse: TypeAlias = Union[List[CourseSummary], Dict[str, Any]]

GRAPHQL_QUERY = """
query {
  allCourses {
    id
    name
    courseCode
    term {
        id
        name
        startAt
    }
  }
}
"""


async def get_all_courses(
    term: Annotated[
        Optional[str],
        Field(
            description=(
                "Optional term filter, e.g. 'Fall 2025'. "
                "When omitted, courses from all terms are returned."
            ),
            pattern=r"^(Fall|Spring|Winter|Summer)\s\d{4}$",
        ),
    ] = None,
) -> CoursesResponse:
    """
    Get all Canvas courses the current user can access, optionally filtered by term.

    Returns a list of course summaries (id, name, course code, term),
    or an error object with "error", "message", and optionally "status_code" keys.
    """
    try:
        response = await canvas_api_client.post_graphql_query(GRAPHQL_QUERY)
        if not isinstance(response.data, dict):
            raise Exception("Response data is not a dictionary")
        data = response.data.get("data", response.data)

        course_list = data["allCourses"]
        courses = [CourseSummary.model_validate(course) for course in course_list]
        if term:
            courses = [
                course
                for course in courses
                if course.term and course.term.name == term
            ]
        return courses

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


get_all_courses_tool: Final[Tool] = Tool.from_function(
    name="get_all_courses",
    description=(
        "List all Canvas courses for the current user with summary fields "
        "(id, name, course code, term). Optionally filter by term name, "
        "e.g. 'Fall 2025'."
    ),
    fn=get_all_courses,
)
