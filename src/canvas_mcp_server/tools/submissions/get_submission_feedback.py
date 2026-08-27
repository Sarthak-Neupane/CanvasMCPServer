"""Tool for fetching feedback on the current user's submission via REST.

Uses GET /api/v1/courses/:course_id/assignments/:assignment_id/submissions/self
"""

from typing import Final, Dict, Any, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import SubmissionFeedback
from ...utils import canvas_api_client, HTTPError
from ._parse import submission_feedback_from_api

SubmissionFeedbackResponse: TypeAlias = Union[SubmissionFeedback, Dict[str, Any]]

FEEDBACK_INCLUDES = [
    "submission_comments",
    "rubric_assessment",
]


async def get_submission_feedback(
    course_id: Annotated[
        str,
        Field(description="The course ID (numeric Canvas ID, e.g. '182571')."),
    ],
    assignment_id: Annotated[
        str,
        Field(description="The assignment ID (numeric Canvas ID)."),
    ],
) -> SubmissionFeedbackResponse:
    """
    Get instructor feedback on the current user's submission.

    Returns submission comments, rubric assessment scores, and file
    attachments. Always scoped to the authenticated user (self only).

    Returns an error object with "error", "message", and optionally
    "status_code" keys on failure.
    """
    try:
        response = await canvas_api_client.get_rest(
            endpoint=(
                f"v1/courses/{course_id}/assignments/"
                f"{assignment_id}/submissions/self"
            ),
            params={"include[]": FEEDBACK_INCLUDES},
        )
        if not isinstance(response.data, dict):
            raise Exception("Canvas submission response was not an object")
        return submission_feedback_from_api(response.data)

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


get_submission_feedback_tool: Final[Tool] = Tool.from_function(
    name="get_submission_feedback",
    description=(
        "Get instructor feedback on your submission for an assignment: "
        "comments, rubric scores, and attachments. Self only."
    ),
    fn=get_submission_feedback,
)
