"""Tool for listing the current user's todo items via the Canvas REST API.

The GraphQL schema does not expose todo items, so this tool uses the REST
endpoint GET /api/v1/users/self/todo.
"""

from typing import Final, Dict, Any, Optional, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import TodoItem, ListResult
from ...utils.list_limits import DEFAULT_LIST_LIMIT, ListLimitField, finalize_list, resolve_list_limit
from ...errors import as_tool_error
from ...utils import canvas_api_client

TodoItemsResponse: TypeAlias = Union[ListResult[TodoItem], Dict[str, Any]]

REST_ENDPOINT = "v1/users/self/todo"


async def get_todo_items(
    course_id: Annotated[
        Optional[str],
        Field(
            description=(
                "Optional course id to scope todos server-side via course_ids[]."
            ),
        ),
    ] = None,
    limit: ListLimitField = DEFAULT_LIST_LIMIT,
) -> TodoItemsResponse:
    """
    List the current user's Canvas todo items.

    Items are either assignments that need submitting soon (students) or
    assignments that need grading (teachers). Returns an error object with
    "error", "message", and optionally "status_code" keys on failure.
    """
    try:
        item_limit = resolve_list_limit(limit)
        params: Dict[str, Any] = {"per_page": 100}
        if course_id:
            params["course_ids[]"] = [course_id]

        paginated = await canvas_api_client.get_rest_paginated(
            endpoint=REST_ENDPOINT,
            params=params,
            max_items=item_limit,
        )
        items = [TodoItem.model_validate(item) for item in paginated.items]
        return finalize_list(items, item_limit, truncated=paginated.truncated)

    except Exception as e:
        return as_tool_error(e, source="canvas_rest")


get_todo_items_tool: Final[Tool] = Tool.from_function(
    name="get_todo_items",
    description=(
        "List the current user's Canvas todo items: assignments that need "
        "submitting soon (students) or grading (teachers). Optional course_id "
        "scopes server-side. Use limit to cap results."
    ),
    fn=get_todo_items,
)
