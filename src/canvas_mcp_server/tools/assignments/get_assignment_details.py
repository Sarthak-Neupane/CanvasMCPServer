"""Tool for fetching details of a single Canvas assignment via the GraphQL API."""

from typing import Annotated, Any, Dict, Final, Optional, TypeAlias, Union

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...errors import as_tool_error, tool_error
from ...errors.codes import ErrorCode
from ...models import AssignmentDetail, AssignmentExternalTool
from ...utils import canvas_api_client, extract_graphql_data
from ...utils.content_metadata import attach_content_metadata

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
    type, accepted submission types, allowed attempts, course, and external-tool
    metadata when hosted outside Canvas, or an error object with "error",
    "message", and optionally "status_code" keys.
    """
    try:
        response = await canvas_api_client.post_graphql_query(
            query=GRAPHQL_QUERY, variables={"assignmentId": assignment_id}
        )
        data = extract_graphql_data(response)
        assignment = data.get("assignment")
        if assignment is None:
            return tool_error(
                ErrorCode.RESOURCE_NOT_FOUND,
                f"Assignment {assignment_id} not found.",
                source="canvas_graphql",
                details={"assignment_id": assignment_id},
            ).to_response()

        sub_types = [
            str(st).lower()
            for st in (
                assignment.get("submissionTypes")
                or assignment.get("submission_types")
                or []
            )
        ]
        is_external_tool = (
            "external_tool" in sub_types or "external_tool_tag_attributes" in assignment
        )
        has_substantive_body = bool(
            assignment.get("description")
            and len(assignment.get("description", "").strip()) > 20
        )
        canvas_content_available = not is_external_tool or has_substantive_body

        raw_ext = assignment.get("external_tool") or assignment.get(
            "external_tool_tag_attributes"
        )
        ext_tool: Optional[AssignmentExternalTool] = None
        if isinstance(raw_ext, dict):
            ext_tool = AssignmentExternalTool.model_validate(raw_ext)
        elif is_external_tool:
            ext_url = assignment.get("url") or assignment.get("htmlUrl")
            ext_tool = AssignmentExternalTool(url=ext_url)

        assignment_dict = dict(assignment)
        assignment_dict["canvas_content_available"] = canvas_content_available
        if ext_tool is not None:
            assignment_dict["external_tool"] = ext_tool

        detail = AssignmentDetail.model_validate(assignment_dict)
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
        "and allowed attempts. For external-tool assignments (e.g. WebAssign, "
        "MindTap, Zybooks), canvas_content_available is false and external_tool "
        "contains launch details."
    ),
    fn=get_assignment_details,
)
