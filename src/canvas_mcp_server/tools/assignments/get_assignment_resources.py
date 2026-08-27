"""Tool for discovering resources linked in a Canvas assignment description."""

from typing import Final, Dict, Any, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import AssignmentResources
from ...errors import as_tool_error
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

        return AssignmentResources(
            course_id=course_id,
            assignment_id=str(data.get("id", assignment_id)),
            assignment_name=data.get("name"),
            resources=resources,
        )

    except Exception as e:
        return as_tool_error(e, source="canvas_rest")


get_assignment_resources_tool: Final[Tool] = Tool.from_function(
    name="get_assignment_resources",
    description=(
        "Discover resources linked in a Canvas assignment description: files, "
        "pages, external URLs, and other course objects. Metadata only — does "
        "not download. Use before download_assignment_files when you need to see "
        "what is embedded."
    ),
    fn=get_assignment_resources,
)
