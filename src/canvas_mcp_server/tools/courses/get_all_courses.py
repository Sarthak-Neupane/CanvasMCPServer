"""Tool for listing all Canvas courses via the GraphQL API."""

from typing import Final, List, Dict, Any, Optional, Union, TypeAlias, Annotated, Set

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


async def _dashboard_course_ids() -> Set[str]:
    """
    Return course ids that appear on the user's Canvas dashboard.

    enrollment_state=active is weaker than this: Canvas can keep old or
    open-ended enrollments marked active long after they leave the dashboard.
    """
    response = await canvas_api_client.get_rest("v1/dashboard/dashboard_cards")
    cards = response.data
    if not isinstance(cards, list):
        raise Exception("Canvas dashboard_cards response was not a list")
    return {str(card["id"]) for card in cards if isinstance(card, dict) and "id" in card}


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
                "When true, return only the courses on the user's Canvas "
                "dashboard (GET /api/v1/dashboard/dashboard_cards). This is "
                "what 'current courses' / 'this semester' usually means. It "
                "is stricter than enrollment_state=active, which can still "
                "include concluded or open-ended enrollments. When false "
                "(default), every course the user can access is returned, "
                "spanning all past and present terms."
            ),
        ),
    ] = False,
) -> CoursesResponse:
    """
    Get Canvas courses for the current user.

    By default, returns every course the user can access across all terms. Set
    active_only=True to return only courses on the Canvas dashboard (not merely
    enrollment_state=active). Both modes can be further narrowed with the term
    filter.

    Returns a list of course summaries (id, name, course code, term),
    or an error object with "error", "message", and optionally "status_code" keys.
    """
    try:
        if active_only:
            # Dashboard cards are the contract for "current" courses. Hydrate
            # with REST /v1/courses (+ term) so summaries keep the same shape
            # as the non-active path.
            dashboard_ids = await _dashboard_course_ids()
            course_list = await canvas_api_client.get_rest_paginated(
                "v1/courses",
                params={
                    "enrollment_state": "active",
                    "include[]": "term",
                    "per_page": 100,
                },
            )
            courses = [
                _rest_course_to_summary(course)
                for course in course_list
                if isinstance(course, dict)
                and str(course.get("id")) in dashboard_ids
                and not course.get("access_restricted_by_date")
            ]
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
        "courses on the Canvas dashboard (current courses / this semester) — "
        "not every enrollment_state=active course. Optionally filter by term "
        "name, e.g. 'Fall 2025'."
    ),
    fn=get_all_courses,
)
