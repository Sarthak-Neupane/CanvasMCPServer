"""Tool for checking submission status of a Canvas assignment via the GraphQL API."""

from typing import Final, Dict, Any, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import AssignmentSubmissions, SubmissionStatus
from ...errors import as_tool_error
from ...utils import canvas_api_client, extract_graphql_data
from ...utils.graphql_pagination import paginate_graphql_connection
from ._user import current_user_id

SubmissionStatusResponse: TypeAlias = Union[AssignmentSubmissions, Dict[str, Any]]

# Canvas GraphQL does not reliably auto-scope submissionsConnection for
# students — filter to the current user in this tool (student MCP server).
GRAPHQL_QUERY = """
query ($assignmentId: ID!, $first: Int!, $after: String) {
  assignment(id: $assignmentId) {
    _id
    name
    dueAt
    pointsPossible
    submissionsConnection(first: $first, after: $after) {
      nodes {
        _id
        state
        submissionStatus
        gradingStatus
        score
        grade
        excused
        late
        missing
        attempt
        submissionType
        submittedAt
        gradedAt
        cachedDueDate
        user {
          _id
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

PAGE_SIZE = 100


async def get_submission_status(
    assignment_id: Annotated[
        str,
        Field(
            description=(
                "The assignment ID. Accepts either the numeric Canvas ID "
                "(e.g. '987654') or the GraphQL global ID."
            ),
        ),
    ],
) -> SubmissionStatusResponse:
    """
    Get submission status for a Canvas assignment.

    Returns the current user's submission only (status, score, grade,
    late/missing flags, attempt, timestamps). Classmate submissions are
    never returned, even if Canvas expands the connection.

    Returns an error object with "error", "message", and optionally
    "status_code" keys on failure.
    """
    try:
        self_id = await current_user_id()
        assignment_meta: Dict[str, Any] | None = None

        async def fetch_connection(after: str | None) -> Dict[str, Any]:
            nonlocal assignment_meta
            response = await canvas_api_client.post_graphql_query(
                query=GRAPHQL_QUERY,
                variables={
                    "assignmentId": assignment_id,
                    "first": PAGE_SIZE,
                    "after": after,
                },
            )
            data = extract_graphql_data(response)
            assignment = data.get("assignment")
            if assignment is None:
                raise Exception(f"No assignment found for id: {assignment_id}")
            if assignment_meta is None:
                assignment_meta = assignment
            return assignment.get("submissionsConnection") or {"nodes": []}

        nodes = await paginate_graphql_connection(fetch_connection, max_pages=5)
        submissions = [
            SubmissionStatus.model_validate(node)
            for node in nodes
            if str((node.get("user") or {}).get("_id")) == self_id
        ]
        if assignment_meta is None:
            raise Exception(f"No assignment found for id: {assignment_id}")
        return AssignmentSubmissions(
            assignmentId=assignment_meta["_id"],
            assignmentName=assignment_meta.get("name"),
            dueAt=assignment_meta.get("dueAt"),
            pointsPossible=assignment_meta.get("pointsPossible"),
            submissions=submissions,
        )

    except Exception as e:
        return as_tool_error(e, source="canvas_graphql")


get_submission_status_tool: Final[Tool] = Tool.from_function(
    name="get_submission_status",
    description=(
        "Get submission status for a Canvas assignment: whether it was "
        "submitted, when, the score/grade if graded, and late/missing/excused "
        "flags. Returns only the current user's submission."
    ),
    fn=get_submission_status,
)
