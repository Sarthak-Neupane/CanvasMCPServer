"""Tool for listing assignments in a Canvas course via the GraphQL API."""

from typing import Final, List, Dict, Any, Optional, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import AssignmentSummary, ListResult
from ...utils.list_results import list_result
from ...errors import as_tool_error
from ...utils import canvas_api_client, extract_graphql_data
from ...utils.graphql_pagination import (
    DEFAULT_GRAPHQL_MAX_PAGES,
    DEFAULT_GRAPHQL_PAGE_SIZE,
    paginate_graphql_connection,
)

AssignmentsResponse: TypeAlias = Union[ListResult[AssignmentSummary], Dict[str, Any]]

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
            return course["assignmentsConnection"]

        paginated = await paginate_graphql_connection(
            fetch_connection,
            max_pages=DEFAULT_GRAPHQL_MAX_PAGES,
        )
        items = [AssignmentSummary.model_validate(node) for node in paginated.items]
        return list_result(items, truncated=paginated.truncated)

    except Exception as e:
        return as_tool_error(e, source="canvas_graphql")


get_assignments_for_course_tool: Final[Tool] = Tool.from_function(
    name="get_assignments_for_course",
    description=(
        "List all assignments in a Canvas course with summary fields "
        "(id, name, due date, points possible, state, URL)."
    ),
    fn=get_assignments_for_course,
)
