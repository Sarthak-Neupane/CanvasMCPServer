"""Tool for fetching a Canvas course syllabus via the REST API.

Uses GET /api/v1/courses/:course_id with include[]=syllabus_body.
"""

from typing import Final, Dict, Any, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import CourseSyllabus
from ...utils import canvas_api_client, HTTPError

CourseSyllabusResponse: TypeAlias = Union[CourseSyllabus, Dict[str, Any]]


async def get_course_syllabus(
    course_id: Annotated[
        str,
        Field(
            description=(
                "The course ID (numeric Canvas ID, e.g. '182314')."
            ),
        ),
    ],
) -> CourseSyllabusResponse:
    """
    Get the syllabus for a Canvas course.

    Returns course id, name, syllabus_body (HTML), and syllabus_course_summary
    when Canvas provides it. Use this for attendance policy, grading breakdown,
    and other syllabus-only content.

    Returns an error object with "error", "message", and optionally
    "status_code" keys on failure.
    """
    try:
        response = await canvas_api_client.get_rest(
            endpoint=f"v1/courses/{course_id}",
            params={"include[]": "syllabus_body"},
        )
        data = response.data
        if not isinstance(data, dict):
            raise Exception("Canvas course response was not an object")

        return CourseSyllabus(
            course_id=str(data.get("id", course_id)),
            course_name=data.get("name"),
            syllabus_body=data.get("syllabus_body"),
            syllabus_course_summary=data.get("syllabus_course_summary"),
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


get_course_syllabus_tool: Final[Tool] = Tool.from_function(
    name="get_course_syllabus",
    description=(
        "Get a Canvas course syllabus: course name and syllabus_body HTML. "
        "Use for attendance policy, grading weights, exam rules, and other "
        "syllabus-only content."
    ),
    fn=get_course_syllabus,
)
