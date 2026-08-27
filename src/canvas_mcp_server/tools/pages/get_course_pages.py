"""Tool for listing Canvas wiki pages via the REST API.

Uses GET /api/v1/courses/:course_id/pages (metadata only — no body).
"""

from typing import Final, List, Dict, Any, Optional, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import PageSummary
from ...utils import canvas_api_client, HTTPError

PagesResponse: TypeAlias = Union[List[PageSummary], Dict[str, Any]]


async def get_course_pages(
    course_id: Annotated[
        str,
        Field(description="The course ID (numeric Canvas ID, e.g. '182571')."),
    ],
    search_term: Annotated[
        Optional[str],
        Field(
            description=(
                "Optional partial page title filter, e.g. 'Week 4' or 'Syllabus'."
            ),
        ),
    ] = None,
) -> PagesResponse:
    """
    List wiki pages in a Canvas course (metadata only).

    Returns page id, url slug, title, publish state, front-page flag, and lock
    info. Does not include page HTML — call get_page for body content.

    Returns an error object with "error", "message", and optionally
    "status_code" keys on failure.
    """
    try:
        params: Dict[str, Any] = {"per_page": 100}
        if search_term:
            params["search_term"] = search_term

        response = await canvas_api_client.get_rest(
            endpoint=f"v1/courses/{course_id}/pages",
            params=params,
        )
        if not isinstance(response.data, list):
            raise Exception("Canvas pages response was not a list")
        return [PageSummary.model_validate(page) for page in response.data]

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


get_course_pages_tool: Final[Tool] = Tool.from_function(
    name="get_course_pages",
    description=(
        "List wiki pages in a Canvas course (title, url slug, publish state, "
        "front-page flag). Does not return page HTML — use get_page for content. "
        "Optional search_term filters by title."
    ),
    fn=get_course_pages,
)
