"""Tool for fetching one Canvas wiki page via the REST API.

Uses GET /api/v1/courses/:course_id/pages/:url_or_id.
"""

from typing import Final, Dict, Any, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import PageDetail
from ...errors import as_tool_error
from ...utils.content_metadata import attach_content_metadata
from ...utils import canvas_api_client
from ...utils.html import html_to_text
from ._params import page_endpoint_segment

PageResponse: TypeAlias = Union[PageDetail, Dict[str, Any]]


async def get_page(
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
) -> PageResponse:
    """
    Get one Canvas wiki page including HTML body.

    Accepts a page url slug, numeric page id, or a full Canvas pages path.
    Also returns body_text (plain text derived from body HTML).

    Returns an error object with "error", "message", and optionally
    "status_code" keys on failure.
    """
    try:
        segment = page_endpoint_segment(page_id_or_url)
        response = await canvas_api_client.get_rest(
            endpoint=f"v1/courses/{course_id}/pages/{segment}",
        )
        if not isinstance(response.data, dict):
            raise Exception("Canvas page response was not an object")

        detail = PageDetail.model_validate(response.data)
        if detail.body:
            detail = detail.model_copy(update={"body_text": html_to_text(detail.body)})
        resource_id = detail.url or (
            str(detail.page_id) if detail.page_id is not None else segment
        )
        return attach_content_metadata(
            detail,
            source_type="page",
            course_id=course_id,
            resource_id=resource_id,
        )

    except Exception as e:
        return as_tool_error(e, source="canvas_rest")


get_page_tool: Final[Tool] = Tool.from_function(
    name="get_page",
    description=(
        "Get one Canvas wiki page by url slug, numeric id, or full pages path. "
        "Returns title, HTML body, and plain-text body_text."
    ),
    fn=get_page,
)
