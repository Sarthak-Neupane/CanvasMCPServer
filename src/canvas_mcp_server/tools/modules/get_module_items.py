"""Tool for listing items in a Canvas module via the REST API.

Uses GET /api/v1/courses/:course_id/modules/:module_id/items. Keeps the list
lean (no content_details); use get_module_item_details for locks/due dates.
"""

from typing import Final, List, Dict, Any, Optional, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import ModuleItemSummary, ListResult
from ...utils.list_results import list_result
from ...errors import as_tool_error
from ...utils import canvas_api_client

ModuleItemsResponse: TypeAlias = Union[ListResult[ModuleItemSummary], Dict[str, Any]]


async def get_module_items(
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
    search_term: Annotated[
        Optional[str],
        Field(
            description=(
                "Optional partial item title filter, e.g. 'formula' or 'quiz'."
            ),
        ),
    ] = None,
) -> ModuleItemsResponse:
    """
    List items in a Canvas course module.

    Returns type, title, position, content_id, URLs, and completion_requirement
    (including completed for students). Does not include content_details —
    call get_module_item_details for lock/due/points info.

    Returns an error object with "error", "message", and optionally
    "status_code" keys on failure.
    """
    try:
        params: Dict[str, Any] = {"per_page": 100}
        if search_term:
            params["search_term"] = search_term

        paginated = await canvas_api_client.get_rest_paginated(
            endpoint=f"v1/courses/{course_id}/modules/{module_id}/items",
            params=params,
        )
        items = [ModuleItemSummary.model_validate(item) for item in paginated.items]
        return list_result(items, truncated=paginated.truncated)

    except Exception as e:
        return as_tool_error(e, source="canvas_rest")


get_module_items_tool: Final[Tool] = Tool.from_function(
    name="get_module_items",
    description=(
        "List items in a Canvas module (File, Page, Assignment, Quiz, etc.) "
        "with titles, types, positions, and completion requirements. Use after "
        "get_course_modules. Optional search_term filters by item title. For "
        "lock/due/points details on one item, call get_module_item_details."
    ),
    fn=get_module_items,
)
