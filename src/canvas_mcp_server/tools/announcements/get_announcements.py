"""Tool for listing announcements in a Canvas course via the GraphQL API."""

from typing import Final, List, Dict, Any, Optional, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import Announcement, ListResult
from ...utils.content_metadata import attach_content_metadata
from ...utils.list_results import list_result
from ...errors import as_tool_error
from ...utils import canvas_api_client, extract_graphql_data
from ...utils.graphql_pagination import (
    DEFAULT_GRAPHQL_MAX_PAGES,
    DEFAULT_GRAPHQL_PAGE_SIZE,
    paginate_graphql_connection,
)

AnnouncementsResponse: TypeAlias = Union[ListResult[Announcement], Dict[str, Any]]

GRAPHQL_QUERY = """
query ($courseId: ID!, $first: Int!, $after: String) {
  course(id: $courseId) {
    discussionsConnection(
      first: $first
      after: $after
      filter: {isAnnouncement: true}
    ) {
      nodes {
        _id
        title
        message
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
) -> AnnouncementsResponse:
    """
    List announcements in a Canvas course, most recent first.

    Returns announcement title, message (HTML), post date, and author,
    or an error object with "error", "message", and optionally
    "status_code" keys.
    """
    try:
        async def fetch_connection(after: Optional[str]) -> Dict[str, Any]:
            response = await canvas_api_client.post_graphql_query(
                query=GRAPHQL_QUERY,
                variables={
                    "courseId": course_id,
                    "first": DEFAULT_GRAPHQL_PAGE_SIZE,
                    "after": after,
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
        )
        items = [
            attach_content_metadata(
                Announcement.model_validate(node),
                source_type="announcement",
                course_id=course_id,
                resource_id=str(node.get("_id")),
            )
            for node in paginated.items
        ]
        return list_result(items, truncated=paginated.truncated)

    except Exception as e:
        return as_tool_error(e, source="canvas_graphql")


get_announcements_tool: Final[Tool] = Tool.from_function(
    name="get_announcements",
    description=(
        "List announcements in a Canvas course (title, message, post date, "
        "author), most recent first."
    ),
    fn=get_announcements,
)
