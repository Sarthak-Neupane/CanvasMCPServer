"""Tool for listing all Canvas courses via the GraphQL API."""

from typing import Final, List, Dict, Any, Optional, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import CourseSummary
from ...utils import canvas_api_client, extract_graphql_data, HTTPError

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
        endAt
    }
  }
}
"""


def _rest_course_to_summary(course: Dict[str, Any]) -> CourseSummary:
    """Map a Canvas REST course object (snake_case) to a CourseSummary."""
    raw_term = course.get("term") or {}
    term_data: Optional[Dict[str, Any]] = None
    if raw_term.get("name"):
        term_data = {
            "id": str(raw_term.get("id")),
            "name": raw_term.get("name"),
            "startAt": raw_term.get("start_at"),
            "endAt": raw_term.get("end_at"),
        }
    return CourseSummary.model_validate(
        {
            "id": str(course.get("id")),
            "name": course.get("name"),
            "courseCode": course.get("course_code"),
            "term": term_data,
        }
    )


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
    active_only: Annotated[
        bool,
        Field(
            description=(
                "When true, return only the courses the user is currently "
                "actively enrolled in (enrollment_state=active). This matches "
                "the 'current courses' shown on the Canvas dashboard and is the "
                "right choice for questions like 'what am I taking this "
                "semester?'. When false (default), every course the user can "
                "access is returned, spanning all past and present terms."
            ),
        ),
    ] = False,
) -> CoursesResponse:
    """
    Get Canvas courses for the current user.

    By default, returns every course the user can access across all terms. Set
    active_only=True to return only currently active enrollments (the courses on
    the user's Canvas dashboard), which is what "current"/"this semester" means.
    Both modes can be further narrowed with the term filter.

    Returns a list of course summaries (id, name, course code, term),
    or an error object with "error", "message", and optionally "status_code" keys.
    """
    try:
        if active_only:
            # The GraphQL allCourses field has no active-enrollment filter, so we
            # use the REST courses endpoint, which mirrors the dashboard.
            rest_response = await canvas_api_client.get_rest(
                "v1/courses",
                params={
                    "enrollment_state": "active",
                    "include[]": "term",
                    "per_page": 100,
                },
            )
            course_list = rest_response.data
            if not isinstance(course_list, list):
                raise Exception("Canvas REST courses response was not a list")
            courses = [_rest_course_to_summary(course) for course in course_list]
        else:
            response = await canvas_api_client.post_graphql_query(GRAPHQL_QUERY)
            data = extract_graphql_data(response)
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
        "List Canvas courses for the current user with summary fields "
        "(id, name, course code, term). Set active_only=true to return only "
        "the user's currently active courses (what shows on the Canvas "
        "dashboard) -- use this for 'my current courses' or 'what am I taking "
        "this semester'. Optionally filter by term name, e.g. 'Fall 2025'."
    ),
    fn=get_all_courses,
)
