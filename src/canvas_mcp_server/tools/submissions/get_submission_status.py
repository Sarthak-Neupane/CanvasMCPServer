"""Tool for checking submission status of a Canvas assignment via the GraphQL API."""

from typing import Final, Dict, Any, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import AssignmentSubmissions, SubmissionStatus
from ...utils import canvas_api_client, extract_graphql_data, HTTPError
from ._user import current_user_id

SubmissionStatusResponse: TypeAlias = Union[AssignmentSubmissions, Dict[str, Any]]

# Canvas GraphQL does not reliably auto-scope submissionsConnection for
# students — filter to the current user in this tool (student MCP server).
GRAPHQL_QUERY = """
query ($assignmentId: ID!, $first: Int!) {
  assignment(id: $assignmentId) {
    _id
    name
    dueAt
    pointsPossible
    submissionsConnection(first: $first) {
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
        response = await canvas_api_client.post_graphql_query(
            query=GRAPHQL_QUERY,
            variables={"assignmentId": assignment_id, "first": PAGE_SIZE},
        )
        data = extract_graphql_data(response)
        assignment = data.get("assignment")
        if assignment is None:
            raise Exception(f"No assignment found for id: {assignment_id}")

        connection = assignment.get("submissionsConnection") or {"nodes": []}
        submissions = [
            SubmissionStatus.model_validate(node)
            for node in connection["nodes"]
            if str((node.get("user") or {}).get("_id")) == self_id
        ]
        return AssignmentSubmissions(
            assignmentId=assignment["_id"],
            assignmentName=assignment.get("name"),
            dueAt=assignment.get("dueAt"),
            pointsPossible=assignment.get("pointsPossible"),
            submissions=submissions,
        )

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


get_submission_status_tool: Final[Tool] = Tool.from_function(
    name="get_submission_status",
    description=(
        "Get submission status for a Canvas assignment: whether it was "
        "submitted, when, the score/grade if graded, and late/missing/excused "
        "flags. Returns only the current user's submission."
    ),
    fn=get_submission_status,
)
