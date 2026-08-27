"""Tool for fetching Canvas discussion replies via the REST API.

Uses GET /api/v1/courses/:course_id/discussion_topics/:topic_id/view.
"""

from typing import Annotated, Any, Dict, Final, TypeAlias, Union

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...errors import as_discussion_tool_error
from ...models import DiscussionEntries
from ...utils import canvas_api_client
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

    On failure returns a structured error object (see docs/errors.md).
    """
    try:
        response = await canvas_api_client.get_rest(
            endpoint=(
                f"v1/courses/{course_id}/discussion_topics/" f"{discussion_id}/view"
            ),
        )
        if not isinstance(response.data, dict):
            raise Exception("Canvas discussion view response was not an object")
        return discussion_entries_from_view(
            response.data,
            course_id=course_id,
            discussion_id=discussion_id,
        )

    except Exception as e:
        return as_discussion_tool_error(e, source="canvas_rest")


get_discussion_entries_tool: Final[Tool] = Tool.from_function(
    name="get_discussion_entries",
    description=(
        "List replies in a Canvas discussion topic with threaded nesting. "
        "Returns a clear lock error when an initial post is required before "
        "viewing other replies."
    ),
    fn=get_discussion_entries,
)
