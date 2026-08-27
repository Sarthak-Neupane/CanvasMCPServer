"""Tool for fetching one Canvas module item with content_details via REST.

Uses GET /api/v1/courses/:course_id/modules/:module_id/items/:id with
include[]=content_details.
"""

from typing import Final, Dict, Any, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import ModuleItemDetail
from ...utils import canvas_api_client, HTTPError

ModuleItemDetailsResponse: TypeAlias = Union[ModuleItemDetail, Dict[str, Any]]


async def get_module_item_details(
    course_id: Annotated[
        str,
        Field(
            description=(
                "The course ID (numeric Canvas ID, e.g. '182571')."
            ),
        ),
    ],
    module_id: Annotated[
        str,
        Field(
            description=(
                "The module ID (numeric Canvas ID from get_course_modules)."
            ),
        ),
    ],
    item_id: Annotated[
        str,
        Field(
            description=(
                "The module item ID (numeric Canvas ID from get_module_items)."
            ),
        ),
    ],
) -> ModuleItemDetailsResponse:
    """
    Get details for a single Canvas module item.

    Includes content_details when Canvas provides them (points, due/unlock/lock
    dates, locked_for_user, lock_explanation). Also returns completion
    requirements and standard item fields.

    Returns an error object with "error", "message", and optionally
    "status_code" keys on failure.
    """
    try:
        response = await canvas_api_client.get_rest(
            endpoint=(
                f"v1/courses/{course_id}/modules/{module_id}/items/{item_id}"
            ),
            params={"include[]": "content_details"},
        )
        if not isinstance(response.data, dict):
            raise Exception("Canvas module item response was not an object")
        return ModuleItemDetail.model_validate(response.data)

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


get_module_item_details_tool: Final[Tool] = Tool.from_function(
    name="get_module_item_details",
    description=(
        "Get one Canvas module item with content_details (points, due/lock "
        "dates, lock explanation) plus completion requirements. Use after "
        "get_module_items when you need lock or due-date detail for a specific "
        "item."
    ),
    fn=get_module_item_details,
)
