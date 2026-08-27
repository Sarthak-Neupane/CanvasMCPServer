"""Tool for fetching Canvas discussion replies via the REST API.

Uses GET /api/v1/courses/:course_id/discussion_topics/:topic_id/view.
"""

from typing import Final, Dict, Any, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import DiscussionEntries
from ...utils import canvas_api_client, HTTPError
from ._errors import discussion_http_error
from ._parse import discussion_entries_from_view

DiscussionEntriesResponse: TypeAlias = Union[DiscussionEntries, Dict[str, Any]]


async def get_discussion_entries(
    course_id: Annotated[
        str,
        Field(description="The course ID (numeric Canvas ID, e.g. '182571')."),
    ],
    discussion_id: Annotated[
        str,
        Field(description="The numeric Canvas discussion topic id."),
    ],
) -> DiscussionEntriesResponse:
    """
    List replies in a Canvas discussion topic (threaded when applicable).

    Returns entries with nested replies, participant names, and unread ids.
    When the topic requires an initial post, returns a Discussion Locked
    error with lock_reason=require_initial_post instead of a generic 403.

    Returns an error object with "error", "message", and optionally
    "status_code" keys on failure.
    """
    try:
        response = await canvas_api_client.get_rest(
            endpoint=(
                f"v1/courses/{course_id}/discussion_topics/"
                f"{discussion_id}/view"
            ),
        )
        if not isinstance(response.data, dict):
            raise Exception("Canvas discussion view response was not an object")
        return discussion_entries_from_view(response.data)

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


get_discussion_entries_tool: Final[Tool] = Tool.from_function(
    name="get_discussion_entries",
    description=(
        "List replies in a Canvas discussion topic with threaded nesting. "
        "Returns a clear lock error when an initial post is required before "
        "viewing other replies."
    ),
    fn=get_discussion_entries,
)
