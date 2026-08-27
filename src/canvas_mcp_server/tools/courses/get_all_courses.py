"""Tool for listing all Canvas courses via the GraphQL API."""

from __future__ import annotations

import asyncio
from typing import Annotated, Any, Dict, Final, List, Optional, TypeAlias, Union

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...errors import as_tool_error
from ...models import CourseSummary, ListResult
from ...utils import canvas_api_client, extract_graphql_data
from ...utils.dashboard import dashboard_course_ids
from ...utils.list_limits import (
    DEFAULT_LIST_LIMIT,
    ListLimitField,
    cap_items,
    finalize_list,
    resolve_list_limit,
)

CoursesResponse: TypeAlias = Union[ListResult[CourseSummary], Dict[str, Any]]

GRAPHQL_QUERY = """
query {
  allCourses {
    id
    name
    courseCode
    term {
        id
        _id
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


async def _fetch_rest_course_summary(course_id: str) -> Optional[CourseSummary]:
    response = await canvas_api_client.get_rest(
        f"v1/courses/{course_id}",
        params={"include[]": "term"},
    )
    data = response.data
    if not isinstance(data, dict):
        return None
    if data.get("access_restricted_by_date"):
        return None
    return _rest_course_to_summary(data)


async def _term_id_for_name(term_name: str) -> Optional[str]:
    """Resolve a REST enrollment_term_id from a human term name."""
    response = await canvas_api_client.post_graphql_query(query=GRAPHQL_QUERY)
    data = extract_graphql_data(response)
    for course in data.get("allCourses") or []:
        if not isinstance(course, dict):
            continue
        term = course.get("term") or {}
        if term.get("name") != term_name:
            continue
        term_id = term.get("_id") or term.get("id")
        if term_id is not None:
            return str(term_id)
    return None


async def _courses_for_term(
    term_name: str, limit: int
) -> tuple[List[CourseSummary], bool]:
    term_id = await _term_id_for_name(term_name)
    if term_id is None:
        return [], False
    paginated = await canvas_api_client.get_rest_paginated(
        "v1/courses",
        params={
            "enrollment_term_id": term_id,
            "include[]": "term",
            "per_page": 100,
        },
        max_items=limit,
    )
    courses = [
        _rest_course_to_summary(course)
        for course in paginated.items
        if isinstance(course, dict)
    ]
    return courses, paginated.truncated


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
    limit: ListLimitField = DEFAULT_LIST_LIMIT,
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
        item_limit = resolve_list_limit(limit)
        truncated = False

        if active_only:
            dashboard_ids = sorted(await dashboard_course_ids())
            if len(dashboard_ids) > item_limit:
                truncated = True
            fetch_ids = dashboard_ids[:item_limit]
            summaries = await asyncio.gather(
                *[_fetch_rest_course_summary(course_id) for course_id in fetch_ids]
            )
            courses = [course for course in summaries if course is not None]
            if term:
                courses = [
                    course
                    for course in courses
                    if course.term and course.term.name == term
                ]
            return finalize_list(courses, item_limit, truncated=truncated)

        if term:
            courses, truncated = await _courses_for_term(term, item_limit)
            return finalize_list(courses, item_limit, truncated=truncated)

        response = await canvas_api_client.post_graphql_query(GRAPHQL_QUERY)
        data = extract_graphql_data(response)
        course_list = data["allCourses"]
        courses = [CourseSummary.model_validate(course) for course in course_list]
        capped, cut = cap_items(courses, item_limit)
        return finalize_list(capped, item_limit, truncated=cut)

    except Exception as e:
        return as_tool_error(e, source="canvas_graphql")


get_all_courses_tool: Final[Tool] = Tool.from_function(
    name="get_all_courses",
    description=(
        "List Canvas courses for the current user with summary fields "
        "(id, name, course code, term). Set active_only=true to return only "
        "courses on the Canvas dashboard (current courses / this semester) — "
        "not every enrollment_state=active course. Optionally filter by term "
        "name, e.g. 'Fall 2025'. Use limit to cap how many courses are returned."
    ),
    fn=get_all_courses,
)
