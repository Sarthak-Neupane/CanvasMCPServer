"""Tool for listing Canvas discussion topics via the REST API.

Uses GET /api/v1/courses/:course_id/discussion_topics.
"""

from typing import Final, List, Dict, Any, Optional, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import DiscussionSummary
from ...utils import canvas_api_client, HTTPError

DiscussionsResponse: TypeAlias = Union[List[DiscussionSummary], Dict[str, Any]]


async def get_course_discussions(
    course_id: Annotated[
        str,
        Field(description="The course ID (numeric Canvas ID, e.g. '182571')."),
    ],
    search_term: Annotated[
        Optional[str],
        Field(
            description=(
                "Optional partial title filter, e.g. 'Week 1' or 'Lab'."
            ),
        ),
    ] = None,
) -> DiscussionsResponse:
    """
    List discussion topics in a Canvas course (not announcements).

    Returns title, dates, lock state, require_initial_post, reply counts,
    and html_url. Does not include replies — use get_discussion_entries.

    Returns an error object with "error", "message", and optionally
    "status_code" keys on failure.
    """
    try:
        params: Dict[str, Any] = {
            "per_page": 100,
            "only_announcements": False,
        }
        if search_term:
            params["search_term"] = search_term

        data = await canvas_api_client.get_rest_paginated(
            endpoint=f"v1/courses/{course_id}/discussion_topics",
            params=params,
        )
        return [DiscussionSummary.model_validate(topic) for topic in data]

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


get_course_discussions_tool: Final[Tool] = Tool.from_function(
    name="get_course_discussions",
    description=(
        "List discussion topics in a Canvas course (excluding announcements). "
        "Returns lock state and whether an initial post is required before "
        "viewing replies. Optional search_term filters by title."
    ),
    fn=get_course_discussions,
)
