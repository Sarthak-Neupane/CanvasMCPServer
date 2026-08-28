"""Tool for discovering resources linked in a Canvas wiki page."""

from typing import Annotated, Any, Dict, Final, Optional, TypeAlias, Union

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...errors import as_tool_error
from ...models import PageResources
from ...utils import canvas_api_client
from ..assignments._resources import parse_assignment_resources_from_html
from ._params import page_endpoint_segment

PageResourcesResponse: TypeAlias = Union[PageResources, Dict[str, Any]]


async def get_page_resources(
    course_id: Annotated[
        str,
        Field(description="The course ID (numeric Canvas ID, e.g. '182571')."),
    ],
    page_id_or_url: Annotated[
        str,
        Field(
            description=(
                "The page url slug (e.g. 'week-1'), numeric page id, or full "
                "Canvas path like '/courses/123/pages/week-1'."
            ),
        ),
    ],
) -> PageResourcesResponse:
    """
    List Canvas resources linked in a wiki page's body HTML.

    Discovers embedded files, pages, external URLs, assignments, quizzes,
    discussions, and other course objects from anchor hrefs and instructure
    ``data-api-endpoint`` attributes. Does not download files — use download_file
    or batch download tools.

    Returns an error object with "error", "message", and optionally
    "status_code" keys on failure.
    """
    try:
        segment = page_endpoint_segment(page_id_or_url)
        response = await canvas_api_client.get_rest(
            endpoint=f"v1/courses/{course_id}/pages/{segment}",
        )
        data = response.data
        if not isinstance(data, dict):
            raise Exception("Canvas page response was not an object")

        body = data.get("body") or ""
        resources = parse_assignment_resources_from_html(
            body,
            default_course_id=course_id,
        )

        status = "ok"
        empty_reason: Optional[str] = None
        if len(resources) == 0:
            status = "empty"
            empty_reason = "No embedded links or files found in page body HTML."

        return PageResources(
            status=status,
            empty_reason=empty_reason,
            course_id=course_id,
            page_url=str(data.get("url", segment)),
            page_title=data.get("title"),
            resources=resources,
            result_count=len(resources),
        )

    except Exception as e:
        return as_tool_error(e, source="canvas_rest")


get_page_resources_tool: Final[Tool] = Tool.from_function(
    name="get_page_resources",
    description=(
        "Discover resources linked in a Canvas wiki page: files, pages, "
        "assignments, quizzes, discussions, external URLs, and modules. "
        "Metadata only — does not download. Use before download_file when "
        "you need to see what is linked or embedded on a lecture/content page."
    ),
    fn=get_page_resources,
)
