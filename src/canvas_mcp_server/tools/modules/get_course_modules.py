"""Tool for listing Canvas course modules via the REST API.

Uses GET /api/v1/courses/:course_id/modules. Returns structure only — never
requests include[]=items (use get_module_items for item inventory).
"""

from typing import Final, List, Dict, Any, Optional, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import ModuleSummary
from ...utils import canvas_api_client, HTTPError

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

        response = await canvas_api_client.get_rest(
            endpoint=f"v1/courses/{course_id}/modules",
            params=params,
        )
        if not isinstance(response.data, list):
            raise Exception("Canvas modules response was not a list")
        return [ModuleSummary.model_validate(module) for module in response.data]

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


get_course_modules_tool: Final[Tool] = Tool.from_function(
    name="get_course_modules",
    description=(
        "List modules in a Canvas course (structure only: name, position, "
        "unlock date, item count, student progression state). Does not return "
        "module items or download files — use get_module_items next. Optional "
        "search_term filters by module name."
    ),
    fn=get_course_modules,
)
