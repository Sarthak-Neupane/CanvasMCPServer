"""Tool for listing assignments in a Canvas course via the GraphQL API."""

from typing import Annotated, Any, Dict, Final, List, Optional, TypeAlias, Union

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...errors import as_tool_error
from ...models import AssignmentSummary, ListResult
from ...utils import canvas_api_client, extract_graphql_data
from ...utils.graphql_pagination import (
    DEFAULT_GRAPHQL_MAX_PAGES,
    DEFAULT_GRAPHQL_PAGE_SIZE,
    paginate_graphql_connection,
)
from ...utils.list_limits import (
    DEFAULT_LIST_LIMIT,
    ListLimitField,
    finalize_list,
    resolve_list_limit,
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
    limit: ListLimitField = DEFAULT_LIST_LIMIT,
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
            connection = course.get("assignmentsConnection")
            if not isinstance(connection, dict):
                raise Exception("Canvas assignmentsConnection was not an object")
            return connection

        item_limit = resolve_list_limit(limit)
        paginated = await paginate_graphql_connection(
            fetch_connection,
            max_pages=DEFAULT_GRAPHQL_MAX_PAGES,
            max_items=item_limit,
        )
        items = [AssignmentSummary.model_validate(node) for node in paginated.items]
        return finalize_list(items, item_limit, truncated=paginated.truncated)

    except Exception as e:
        return as_tool_error(e, source="canvas_graphql")


get_assignments_for_course_tool: Final[Tool] = Tool.from_function(
    name="get_assignments_for_course",
    description=(
        "List all assignments in a Canvas course with summary fields "
        "(id, name, due date, points possible, state, URL). Use limit to cap results."
    ),
    fn=get_assignments_for_course,
)
