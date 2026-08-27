"""Tool for listing Canvas quizzes via the REST API.

Uses GET /api/v1/courses/:course_id/quizzes.
"""

from typing import Annotated, Any, Dict, Final, List, Optional, TypeAlias, Union

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...errors import as_tool_error
from ...models import ListResult, QuizSummary
from ...utils import canvas_api_client
from ...utils.list_limits import (
    DEFAULT_LIST_LIMIT,
    ListLimitField,
    finalize_list,
    resolve_list_limit,
)
from ._parse import sanitize_quiz_api_payload

QuizzesResponse: TypeAlias = Union[ListResult[QuizSummary], Dict[str, Any]]


async def get_course_quizzes(
    course_id: Annotated[
        str,
        Field(description="The course ID (numeric Canvas ID, e.g. '182571')."),
    ],
    search_term: Annotated[
        Optional[str],
        Field(
            description=("Optional partial title filter, e.g. 'Midterm' or 'Quiz 1'."),
        ),
    ] = None,
    limit: ListLimitField = DEFAULT_LIST_LIMIT,
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

        paginated = await canvas_api_client.get_rest_paginated(
            endpoint=f"v1/courses/{course_id}/quizzes",
            params=params,
            max_items=resolve_list_limit(limit),
        )

        items = [
            QuizSummary.model_validate(sanitize_quiz_api_payload(quiz))
            for quiz in paginated.items
            if isinstance(quiz, dict)
        ]
        return finalize_list(
            items, resolve_list_limit(limit), truncated=paginated.truncated
        )

    except Exception as e:
        return as_tool_error(e, source="canvas_rest")


get_course_quizzes_tool: Final[Tool] = Tool.from_function(
    name="get_course_quizzes",
    description=(
        "List quizzes in a Canvas course (metadata only: due dates, time "
        "limits, lock state, question count). Does not return questions. "
        "Optional search_term filters by title."
    ),
    fn=get_course_quizzes,
)
