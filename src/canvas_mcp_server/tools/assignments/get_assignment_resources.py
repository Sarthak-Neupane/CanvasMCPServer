"""Tool for discovering resources linked in a Canvas assignment description."""

from typing import Annotated, Any, Dict, Final, Optional, TypeAlias, Union

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...errors import as_tool_error
from ...models import AssignmentResources
from ...utils import canvas_api_client
from ._resources import parse_assignment_resources_from_html

AssignmentResourcesResponse: TypeAlias = Union[AssignmentResources, Dict[str, Any]]


async def get_assignment_resources(
    course_id: Annotated[
        str,
        Field(description="The course ID (numeric Canvas ID)."),
    ],
    assignment_id: Annotated[
        str,
        Field(description="The assignment ID (numeric Canvas ID)."),
    ],
) -> AssignmentResourcesResponse:
    """
    List Canvas resources linked in an assignment's description HTML.

    Discovers embedded files, pages, external URLs, and other course objects
    from anchor hrefs and instructure ``data-api-endpoint`` attributes.
    Does not download files — use download_file or download_assignment_files.

    Returns an error object with "error", "message", and optionally
    "status_code" keys on failure.
    """
    try:
        response = await canvas_api_client.get_rest(
            f"v1/courses/{course_id}/assignments/{assignment_id}",
        )
        data = response.data
        if not isinstance(data, dict):
            raise Exception("Canvas assignment response was not an object")

        description = data.get("description") or ""
        resources = parse_assignment_resources_from_html(
            description,
            default_course_id=course_id,
        )

        submission_types = data.get("submission_types") or []
        is_external_tool = (
            "external_tool" in submission_types
            or data.get("external_tool_tag_attributes") is not None
        )

        status = "ok"
        empty_reason: Optional[str] = None
        if len(resources) == 0:
            if is_external_tool:
                status = "external_tool"
                empty_reason = (
                    "Assignment content is hosted externally in a third-party tool "
                    "(e.g. WebAssign, MindTap). Canvas does not store embedded file resources."
                )
            else:
                status = "empty"
                empty_reason = (
                    "No embedded links or files found in assignment description HTML."
                )

        return AssignmentResources(
            status=status,
            empty_reason=empty_reason,
            course_id=course_id,
            assignment_id=str(data.get("id", assignment_id)),
            assignment_name=data.get("name"),
            resources=resources,
            result_count=len(resources),
        )

    except Exception as e:
        return as_tool_error(e, source="canvas_rest")


get_assignment_resources_tool: Final[Tool] = Tool.from_function(
    name="get_assignment_resources",
    description=(
        "Discover resources linked in a Canvas assignment description: files, "
        "pages, external URLs, and other course objects. Metadata only — does "
        "not download. Use before download_assignment_files when you need to see "
        "what is embedded. For external-tool assignments (WebAssign, MindTap), "
        "returns status='external_tool' with an explanatory empty_reason."
    ),
    fn=get_assignment_resources,
)
