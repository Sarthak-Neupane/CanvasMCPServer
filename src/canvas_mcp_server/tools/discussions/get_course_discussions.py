"""Tool for listing Canvas discussion topics via the REST API.

Uses GET /api/v1/courses/:course_id/discussion_topics.
"""

from typing import Annotated, Any, Dict, Final, List, Optional, TypeAlias, Union

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...errors import as_tool_error
from ...models import DiscussionSummary, ListResult
from ...utils import canvas_api_client
from ...utils.list_limits import (
    DEFAULT_LIST_LIMIT,
    ListLimitField,
    finalize_list,
    resolve_list_limit,
)

DiscussionsResponse: TypeAlias = Union[ListResult[DiscussionSummary], Dict[str, Any]]


async def get_course_discussions(
    course_id: Annotated[
        str,
        Field(description="The course ID (numeric Canvas ID, e.g. '182571')."),
    ],
    search_term: Annotated[
        Optional[str],
        Field(
            description=("Optional partial title filter, e.g. 'Week 1' or 'Lab'."),
        ),
    ] = None,
    limit: ListLimitField = DEFAULT_LIST_LIMIT,
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

        paginated = await canvas_api_client.get_rest_paginated(
            endpoint=f"v1/courses/{course_id}/discussion_topics",
            params=params,
            max_items=resolve_list_limit(limit),
        )
        items = [DiscussionSummary.model_validate(topic) for topic in paginated.items]
        return finalize_list(
            items, resolve_list_limit(limit), truncated=paginated.truncated
        )

    except Exception as e:
        return as_tool_error(e, source="canvas_rest")


get_course_discussions_tool: Final[Tool] = Tool.from_function(
    name="get_course_discussions",
    description=(
        "List discussion topics in a Canvas course (excluding announcements). "
        "Returns lock state and whether an initial post is required before "
        "viewing replies. Optional search_term filters by title."
    ),
    fn=get_course_discussions,
)
