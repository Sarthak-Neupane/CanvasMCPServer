"""Tool for fetching details of a single Canvas assignment via the GraphQL API."""

from typing import Final, Dict, Any, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import AssignmentDetail
from ...errors import as_tool_error
from ...utils.content_metadata import attach_content_metadata
from ...utils import canvas_api_client, extract_graphql_data

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
        detail = AssignmentDetail.model_validate(assignment)
        course_id = str((assignment.get("course") or {}).get("_id") or "")
        return attach_content_metadata(
            detail,
            source_type="assignment",
            course_id=course_id or str(detail.id),
            resource_id=str(detail.id),
            canvas_url=detail.htmlUrl,
        )

    except Exception as e:
        return as_tool_error(e, source="canvas_graphql")


get_assignment_details_tool: Final[Tool] = Tool.from_function(
    name="get_assignment_details",
    description=(
        "Get detailed information about a single Canvas assignment by its ID: "
        "description, due/lock dates, points, grading type, submission types, "
        "and allowed attempts."
    ),
    fn=get_assignment_details,
)
