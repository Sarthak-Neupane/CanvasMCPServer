"""Tool for listing the current user's upcoming assignments via the Canvas REST API.

The GraphQL schema does not expose upcoming events, so this tool uses the
REST endpoint GET /api/v1/users/self/upcoming_events and keeps only the
entries that carry an assignment.
"""

from typing import Final, List, Dict, Any, Union, TypeAlias

from mcp.server.fastmcp.tools import Tool

from ...models import UpcomingAssignment, ListResult
from ...utils.list_results import list_result
from ...errors import as_tool_error
from ...utils import canvas_api_client

UpcomingAssignmentsResponse: TypeAlias = Union[ListResult[UpcomingAssignment], Dict[str, Any]]

REST_ENDPOINT = "v1/users/self/upcoming_events"


async def get_upcoming_assignments() -> UpcomingAssignmentsResponse:
    """
    List the current user's upcoming Canvas assignments across all courses.

    Upcoming calendar events that are not assignments are excluded. Returns
    an error object with "error", "message", and optionally "status_code"
    keys on failure.
    """
    try:
        paginated = await canvas_api_client.get_rest_paginated(
            endpoint=REST_ENDPOINT, params={"per_page": 100}
        )

        assignments: List[UpcomingAssignment] = []
        for event in paginated.items:
            assignment = event.get("assignment")
            if not assignment:
                continue
            assignments.append(
                UpcomingAssignment.model_validate(
                    {**assignment, "context_code": event.get("context_code")}
                )
            )
        return list_result(assignments, truncated=paginated.truncated)

    except Exception as e:
        return as_tool_error(e, source="canvas_rest")


get_upcoming_assignments_tool: Final[Tool] = Tool.from_function(
    name="get_upcoming_assignments",
    description=(
        "List the current user's upcoming Canvas assignments across all "
        "courses, with due dates, points, and links."
    ),
    fn=get_upcoming_assignments,
)
