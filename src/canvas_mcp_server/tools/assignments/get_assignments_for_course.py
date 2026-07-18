"""Tool for listing assignments in a Canvas course via the GraphQL API."""

from typing import Final, List, Dict, Any, Optional, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import AssignmentSummary
from ...utils import canvas_api_client, extract_graphql_data, HTTPError

AssignmentsResponse: TypeAlias = Union[List[AssignmentSummary], Dict[str, Any]]

# Relay cursor pagination; pages are fetched until exhausted (capped below).
GRAPHQL_QUERY = """
query ($courseId: ID!, $first: Int!, $after: String) {
  course(id: $courseId) {
    assignmentsConnection(first: $first, after: $after) {
      nodes {
        _id
        name
        dueAt
        pointsPossible
        state
        htmlUrl
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}
"""

PAGE_SIZE = 50
MAX_PAGES = 10


async def get_assignments_for_course(
    course_id: Annotated[
        str,
        Field(
            description=(
                "The course ID. Accepts either the numeric Canvas ID "
                "(e.g. '123456') or the GraphQL global ID."
            ),
        ),
    ],
) -> AssignmentsResponse:
    """
    List all assignments in a Canvas course.

    Returns assignment summaries (id, name, due date, points possible, state,
    URL), or an error object with "error", "message", and optionally
    "status_code" keys.
    """
    try:
        assignments: List[AssignmentSummary] = []
        after: Optional[str] = None
        for _ in range(MAX_PAGES):
            response = await canvas_api_client.post_graphql_query(
                query=GRAPHQL_QUERY,
                variables={"courseId": course_id, "first": PAGE_SIZE, "after": after},
            )
            data = extract_graphql_data(response)
            course = data.get("course")
            if course is None:
                raise Exception(f"No course found for id: {course_id}")

            connection = course["assignmentsConnection"]
            assignments.extend(
                AssignmentSummary.model_validate(node)
                for node in connection["nodes"]
            )
            page_info = connection["pageInfo"]
            if not page_info["hasNextPage"]:
                break
            after = page_info["endCursor"]
        return assignments

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


get_assignments_for_course_tool: Final[Tool] = Tool.from_function(
    name="get_assignments_for_course",
    description=(
        "List all assignments in a Canvas course with summary fields "
        "(id, name, due date, points possible, state, URL)."
    ),
    fn=get_assignments_for_course,
)
