"""Tool for fetching a Canvas assignment rubric via the REST API.

Uses GET /api/v1/courses/:course_id/assignments/:assignment_id
with include[]=rubric.
"""

from typing import Final, Dict, Any, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import Rubric
from ...utils import canvas_api_client, HTTPError
from ._parse import rubric_from_assignment

RubricResponse: TypeAlias = Union[Rubric, Dict[str, Any]]


async def get_assignment_rubric(
    course_id: Annotated[
        str,
        Field(description="The course ID (numeric Canvas ID, e.g. '182571')."),
    ],
    assignment_id: Annotated[
        str,
        Field(description="The assignment ID (numeric Canvas ID)."),
    ],
) -> RubricResponse:
    """
    Get the rubric for a Canvas assignment.

    Returns criteria and rating levels (no student assessment scores).
    When the assignment has no rubric, returns a Not Found error object.

    Returns an error object with "error", "message", and optionally
    "status_code" keys on failure.
    """
    try:
        response = await canvas_api_client.get_rest(
            endpoint=f"v1/courses/{course_id}/assignments/{assignment_id}",
            params={"include[]": "rubric"},
        )
        if not isinstance(response.data, dict):
            raise Exception("Canvas assignment response was not an object")

        rubric = rubric_from_assignment(response.data)
        if rubric is None:
            return {
                "error": "Not Found",
                "message": "This assignment has no rubric.",
            }
        return rubric

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


get_assignment_rubric_tool: Final[Tool] = Tool.from_function(
    name="get_assignment_rubric",
    description=(
        "Get the rubric for a Canvas assignment: criteria, rating levels, "
        "and whether it is used for grading. Does not return student scores."
    ),
    fn=get_assignment_rubric,
)
