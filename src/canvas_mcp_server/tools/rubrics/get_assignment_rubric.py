"""Tool for fetching a Canvas assignment rubric via the REST API.

Uses GET /api/v1/courses/:course_id/assignments/:assignment_id
with include[]=rubric.
"""

from typing import Annotated, Any, Dict, Final, TypeAlias, Union

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...errors import ErrorCode, as_tool_error, tool_error
from ...models import Rubric
from ...utils import canvas_api_client
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
    When the assignment has no rubric, returns a structured not-found error.

    On failure returns a structured error object (see docs/errors.md).
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
            return tool_error(
                ErrorCode.RUBRIC_NOT_FOUND,
                "This assignment has no rubric.",
                source="canvas_rest",
                details={
                    "reason": "no_rubric",
                    "status": "not_applicable",
                    "assignment_id": assignment_id,
                },
            ).to_response()
        return rubric

    except Exception as e:
        return as_tool_error(e, source="canvas_rest")


get_assignment_rubric_tool: Final[Tool] = Tool.from_function(
    name="get_assignment_rubric",
    description=(
        "Get the rubric for a Canvas assignment: criteria, rating levels, "
        "and whether it is used for grading. Does not return student scores."
    ),
    fn=get_assignment_rubric,
)
