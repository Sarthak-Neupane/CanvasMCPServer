"""Tool for listing Canvas course modules via the REST API.

Uses GET /api/v1/courses/:course_id/modules. Returns structure only — never
requests include[]=items (use get_module_items for item inventory).
"""

from typing import Final, List, Dict, Any, Optional, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import ModuleSummary, ListResult
from ...utils.list_limits import DEFAULT_LIST_LIMIT, ListLimitField, finalize_list, resolve_list_limit
from ...errors import as_tool_error
from ...utils import canvas_api_client

ModulesResponse: TypeAlias = Union[List[ModuleSummary], Dict[str, Any]]


async def get_course_modules(
    course_id: Annotated[
        str,
        Field(
            description=(
                "The course ID (numeric Canvas ID, e.g. '182571')."
            ),
        ),
    ],
    search_term: Annotated[
        Optional[str],
        Field(
            description=(
                "Optional partial module name filter, e.g. 'Week 4' or 'Chapter 3'."
            ),
        ),
    ] = None,
    limit: ListLimitField = DEFAULT_LIST_LIMIT,
) -> ModulesResponse:
    """
    List modules in a Canvas course (structure only).

    Returns module id, name, position, unlock date, sequential-progress flag,
    requirement type, prerequisites, item count, workflow state, and (for
    students) progression state / completed_at. Does not embed module items —
    call get_module_items for that.

    Returns an error object with "error", "message", and optionally
    "status_code" keys on failure.
    """
    try:
        params: Dict[str, Any] = {"per_page": 100}
        if search_term:
            params["search_term"] = search_term

        paginated = await canvas_api_client.get_rest_paginated(
            endpoint=f"v1/courses/{course_id}/modules",
            params=params,
            max_items=resolve_list_limit(limit),
        )
        items = [ModuleSummary.model_validate(module) for module in paginated.items]
        return finalize_list(items, resolve_list_limit(limit), truncated=paginated.truncated)

    except Exception as e:
        return as_tool_error(e, source="canvas_rest")


get_course_modules_tool: Final[Tool] = Tool.from_function(
    name="get_course_modules",
    description=(
        "List modules in a Canvas course (structure only: name, position, "
        "unlock date, item count, student progression state). Does not return "
        "module items or download files — use get_module_items next. Optional "
        "search_term filters by module name. Use limit to cap results."
    ),
    fn=get_course_modules,
)
