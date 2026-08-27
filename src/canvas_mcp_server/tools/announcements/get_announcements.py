"""Tool for listing announcements in a Canvas course via the GraphQL API."""

from typing import Final, List, Dict, Any, Optional, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import AnnouncementSummary, ListResult
from ...utils.content_metadata import attach_content_metadata
from ...utils.list_limits import (
    DEFAULT_LIST_LIMIT,
    ListLimitField,
    finalize_list,
    resolve_list_limit,
)
from ...errors import as_tool_error
from ...utils import canvas_api_client, extract_graphql_data
from ...utils.graphql_pagination import (
    DEFAULT_GRAPHQL_MAX_PAGES,
    DEFAULT_GRAPHQL_PAGE_SIZE,
    paginate_graphql_connection,
)

AnnouncementsResponse: TypeAlias = Union[ListResult[AnnouncementSummary], Dict[str, Any]]

GRAPHQL_QUERY = """
query ($courseId: ID!, $first: Int!, $after: String, $searchTerm: String) {
  course(id: $courseId) {
    discussionsConnection(
      first: $first
      after: $after
      filter: {isAnnouncement: true, searchTerm: $searchTerm}
    ) {
      nodes {
        _id
        title
        postedAt
        contextName
        author {
          name
        }
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}
"""


async def get_announcements(
    course_id: Annotated[
        str,
        Field(
            description=(
                "The course ID. Accepts either the numeric Canvas ID "
                "(e.g. '123456') or the GraphQL global ID."
            ),
        ),
    ],
    search_term: Annotated[
        Optional[str],
        Field(
            description="Optional title/body filter passed to Canvas searchTerm.",
        ),
    ] = None,
    limit: ListLimitField = DEFAULT_LIST_LIMIT,
) -> AnnouncementsResponse:
    """
    List announcements in a Canvas course, most recent first.

    Returns announcement metadata (title, post date, author) without HTML bodies.
    Call get_discussion for the full announcement message.

    Returns an error object with "error", "message", and optionally
    "status_code" keys on failure.
    """
    try:
        item_limit = resolve_list_limit(limit)

        async def fetch_connection(after: Optional[str]) -> Dict[str, Any]:
            response = await canvas_api_client.post_graphql_query(
                query=GRAPHQL_QUERY,
                variables={
                    "courseId": course_id,
                    "first": DEFAULT_GRAPHQL_PAGE_SIZE,
                    "after": after,
                    "searchTerm": search_term,
                },
            )
            data = extract_graphql_data(response)
            course = data.get("course")
            if course is None:
                raise Exception(f"No course found for id: {course_id}")
            return course.get("discussionsConnection") or {"nodes": []}

        paginated = await paginate_graphql_connection(
            fetch_connection,
            max_pages=DEFAULT_GRAPHQL_MAX_PAGES,
            max_items=item_limit,
        )
        items = [
            attach_content_metadata(
                AnnouncementSummary.model_validate(node),
                source_type="announcement",
                course_id=course_id,
                resource_id=str(node.get("_id")),
            )
            for node in paginated.items
        ]
        return finalize_list(items, item_limit, truncated=paginated.truncated)

    except Exception as e:
        return as_tool_error(e, source="canvas_graphql")


get_announcements_tool: Final[Tool] = Tool.from_function(
    name="get_announcements",
    description=(
        "List announcements in a Canvas course (title, post date, author) "
        "without HTML bodies — use get_discussion for full message text. "
        "Optional search_term filters server-side. Most recent first."
    ),
    fn=get_announcements,
)
