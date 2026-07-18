"""Tool for fetching details of a single Canvas assignment via the GraphQL API."""

from typing import Final, Dict, Any, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import AssignmentDetail
from ...utils import canvas_api_client, extract_graphql_data, HTTPError

AssignmentDetailResponse: TypeAlias = Union[AssignmentDetail, Dict[str, Any]]

GRAPHQL_QUERY = """
query ($assignmentId: ID!) {
  assignment(id: $assignmentId) {
    _id
    name
    description
    dueAt
    unlockAt
    lockAt
    pointsPossible
    state
    htmlUrl
    gradingType
    submissionTypes
    allowedAttempts
    course {
      _id
      name
    }
  }
}
"""


async def get_assignment_details(
    assignment_id: Annotated[
        str,
        Field(
            description=(
                "The assignment ID. Accepts either the numeric Canvas ID "
                "(e.g. '987654') or the GraphQL global ID."
            ),
        ),
    ],
) -> AssignmentDetailResponse:
    """
    Get detailed information about a single Canvas assignment.

    Returns the assignment's description, due/lock dates, points, grading
    type, accepted submission types, allowed attempts, and course, or an
    error object with "error", "message", and optionally "status_code" keys.
    """
    try:
        response = await canvas_api_client.post_graphql_query(
            query=GRAPHQL_QUERY, variables={"assignmentId": assignment_id}
        )
        data = extract_graphql_data(response)
        assignment = data.get("assignment")
        if assignment is None:
            raise Exception(f"No assignment found for id: {assignment_id}")
        return AssignmentDetail.model_validate(assignment)

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


get_assignment_details_tool: Final[Tool] = Tool.from_function(
    name="get_assignment_details",
    description=(
        "Get detailed information about a single Canvas assignment by its ID: "
        "description, due/lock dates, points, grading type, submission types, "
        "and allowed attempts."
    ),
    fn=get_assignment_details,
)
