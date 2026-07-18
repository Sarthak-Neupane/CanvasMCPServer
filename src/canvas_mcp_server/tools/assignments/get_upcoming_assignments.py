"""Tool for listing the current user's upcoming assignments via the Canvas REST API.

The GraphQL schema does not expose upcoming events, so this tool uses the
REST endpoint GET /api/v1/users/self/upcoming_events and keeps only the
entries that carry an assignment.
"""

from typing import Final, List, Dict, Any, Union, TypeAlias

from mcp.server.fastmcp.tools import Tool

from ...models import UpcomingAssignment
from ...utils import canvas_api_client, HTTPError

UpcomingAssignmentsResponse: TypeAlias = Union[List[UpcomingAssignment], Dict[str, Any]]

REST_ENDPOINT = "v1/users/self/upcoming_events"


async def get_upcoming_assignments() -> UpcomingAssignmentsResponse:
    """
    List the current user's upcoming Canvas assignments across all courses.

    Upcoming calendar events that are not assignments are excluded. Returns
    an error object with "error", "message", and optionally "status_code"
    keys on failure.
    """
    try:
        response = await canvas_api_client.get_rest(
            endpoint=REST_ENDPOINT, params={"per_page": 100}
        )
        if not isinstance(response.data, list):
            raise Exception("Canvas upcoming events response was not a list")

        assignments: List[UpcomingAssignment] = []
        for event in response.data:
            assignment = event.get("assignment")
            if not assignment:
                continue
            assignments.append(
                UpcomingAssignment.model_validate(
                    {**assignment, "context_code": event.get("context_code")}
                )
            )
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


get_upcoming_assignments_tool: Final[Tool] = Tool.from_function(
    name="get_upcoming_assignments",
    description=(
        "List the current user's upcoming Canvas assignments across all "
        "courses, with due dates, points, and links."
    ),
    fn=get_upcoming_assignments,
)
