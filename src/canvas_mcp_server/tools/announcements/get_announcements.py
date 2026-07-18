"""Tool for listing announcements in a Canvas course via the GraphQL API."""

from typing import Final, List, Dict, Any, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import Announcement
from ...utils import canvas_api_client, extract_graphql_data, HTTPError

AnnouncementsResponse: TypeAlias = Union[List[Announcement], Dict[str, Any]]

GRAPHQL_QUERY = """
query ($courseId: ID!, $first: Int!) {
  course(id: $courseId) {
    discussionsConnection(first: $first, filter: {isAnnouncement: true}) {
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
    }
  }
}
"""

PAGE_SIZE = 50


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
        response = await canvas_api_client.post_graphql_query(
            query=GRAPHQL_QUERY,
            variables={"courseId": course_id, "first": PAGE_SIZE},
        )
        data = extract_graphql_data(response)
        course = data.get("course")
        if course is None:
            raise Exception(f"No course found for id: {course_id}")

        connection = course.get("discussionsConnection") or {"nodes": []}
        return [Announcement.model_validate(node) for node in connection["nodes"]]

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


get_announcements_tool: Final[Tool] = Tool.from_function(
    name="get_announcements",
    description=(
        "List announcements in a Canvas course (title, message, post date, "
        "author), most recent first."
    ),
    fn=get_announcements,
)
