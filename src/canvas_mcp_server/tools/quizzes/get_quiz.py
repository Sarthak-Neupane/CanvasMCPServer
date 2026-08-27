"""Tool for fetching one Canvas quiz via the REST API.

Uses GET /api/v1/courses/:course_id/quizzes/:id.
"""

from typing import Annotated, Any, Dict, Final, TypeAlias, Union

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...errors import as_tool_error
from ...models import QuizDetail
from ...utils import canvas_api_client
from ...utils.content_metadata import attach_content_metadata
from ...utils.html import html_to_text
from ._parse import sanitize_quiz_api_payload

QuizResponse: TypeAlias = Union[QuizDetail, Dict[str, Any]]


async def get_quiz(
    course_id: Annotated[
        str,
        Field(description="The course ID (numeric Canvas ID, e.g. '182571')."),
    ],
    quiz_id: Annotated[
        str,
        Field(description="The numeric Canvas quiz id."),
    ],
) -> QuizResponse:
    """
    Get one Canvas quiz (metadata only, no questions).

    Returns instructions, due/unlock/lock dates, time limit, attempt policy,
    and lock state. Does not return question text or answers.

    Returns an error object with "error", "message", and optionally
    "status_code" keys on failure.
    """
    try:
        response = await canvas_api_client.get_rest(
            endpoint=f"v1/courses/{course_id}/quizzes/{quiz_id}",
        )
        if not isinstance(response.data, dict):
            raise Exception("Canvas quiz response was not an object")

        detail = QuizDetail.model_validate(sanitize_quiz_api_payload(response.data))
        if detail.description:
            detail = detail.model_copy(
                update={"description_text": html_to_text(detail.description)}
            )
        return attach_content_metadata(
            detail,
            source_type="quiz",
            course_id=course_id,
            resource_id=str(detail.quiz_id or quiz_id),
            canvas_url=detail.html_url,
        )

    except Exception as e:
        return as_tool_error(e, source="canvas_rest")


get_quiz_tool: Final[Tool] = Tool.from_function(
    name="get_quiz",
    description=(
        "Get one Canvas quiz by id (metadata only: instructions, due dates, "
        "time limit, lock state). Does not return questions."
    ),
    fn=get_quiz,
)
