"""Tool for listing Canvas quizzes via the REST API.

Uses GET /api/v1/courses/:course_id/quizzes.
"""

from typing import Final, List, Dict, Any, Optional, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import QuizSummary
from ...utils import canvas_api_client, HTTPError
from ._parse import sanitize_quiz_api_payload

QuizzesResponse: TypeAlias = Union[List[QuizSummary], Dict[str, Any]]


async def get_course_quizzes(
    course_id: Annotated[
        str,
        Field(description="The course ID (numeric Canvas ID, e.g. '182571')."),
    ],
    search_term: Annotated[
        Optional[str],
        Field(
            description=(
                "Optional partial title filter, e.g. 'Midterm' or 'Quiz 1'."
            ),
        ),
    ] = None,
) -> QuizzesResponse:
    """
    List quizzes in a Canvas course (metadata only, no questions).

    Returns due dates, time limits, attempt limits, lock state, and counts.
    Does not return question text or answers.

    Returns an error object with "error", "message", and optionally
    "status_code" keys on failure.
    """
    try:
        params: Dict[str, Any] = {"per_page": 100}
        if search_term:
            params["search_term"] = search_term

        response = await canvas_api_client.get_rest(
            endpoint=f"v1/courses/{course_id}/quizzes",
            params=params,
        )
        if not isinstance(response.data, list):
            raise Exception("Canvas quizzes response was not a list")

        return [
            QuizSummary.model_validate(sanitize_quiz_api_payload(quiz))
            for quiz in response.data
            if isinstance(quiz, dict)
        ]

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


get_course_quizzes_tool: Final[Tool] = Tool.from_function(
    name="get_course_quizzes",
    description=(
        "List quizzes in a Canvas course (metadata only: due dates, time "
        "limits, lock state, question count). Does not return questions. "
        "Optional search_term filters by title."
    ),
    fn=get_course_quizzes,
)
