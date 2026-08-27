"""Tool for fetching one Canvas discussion topic via the REST API.

Uses GET /api/v1/courses/:course_id/discussion_topics/:topic_id.
"""

from typing import Final, Dict, Any, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import DiscussionDetail
from ...utils import canvas_api_client, HTTPError
from ...utils.html import html_to_text
from ._errors import discussion_http_error

DiscussionResponse: TypeAlias = Union[DiscussionDetail, Dict[str, Any]]


async def get_discussion(
    course_id: Annotated[
        str,
        Field(description="The course ID (numeric Canvas ID, e.g. '182571')."),
    ],
    discussion_id: Annotated[
        str,
        Field(description="The numeric Canvas discussion topic id."),
    ],
) -> DiscussionResponse:
    """
    Get one Canvas discussion topic including the prompt HTML.

    Surfaces lock state (locked_for_user, lock_explanation) and whether the
    user must post before viewing replies (require_initial_post).

    Returns an error object with "error", "message", and optionally
    "status_code" keys on failure.
    """
    try:
        response = await canvas_api_client.get_rest(
            endpoint=(
                f"v1/courses/{course_id}/discussion_topics/{discussion_id}"
            ),
        )
        if not isinstance(response.data, dict):
            raise Exception("Canvas discussion response was not an object")

        detail = DiscussionDetail.model_validate(response.data)
        if detail.message:
            return detail.model_copy(
                update={"message_text": html_to_text(detail.message)}
            )
        return detail

    except HTTPError as e:
        mapped = discussion_http_error(e)
        if mapped:
            return mapped
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


get_discussion_tool: Final[Tool] = Tool.from_function(
    name="get_discussion",
    description=(
        "Get one Canvas discussion topic by id, including prompt HTML, lock "
        "state, and require_initial_post flag."
    ),
    fn=get_discussion,
)
