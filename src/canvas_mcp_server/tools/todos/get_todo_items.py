"""Tool for listing the current user's todo items via the Canvas REST API.

The GraphQL schema does not expose todo items, so this tool uses the REST
endpoint GET /api/v1/users/self/todo.
"""

from typing import Final, List, Dict, Any, Union, TypeAlias

from mcp.server.fastmcp.tools import Tool

from ...models import TodoItem, ListResult
from ...utils.list_results import list_result
from ...errors import as_tool_error
from ...utils import canvas_api_client

TodoItemsResponse: TypeAlias = Union[ListResult[TodoItem], Dict[str, Any]]

REST_ENDPOINT = "v1/users/self/todo"


async def get_todo_items() -> TodoItemsResponse:
    """
    List the current user's Canvas todo items.

    Items are either assignments that need submitting soon (students) or
    assignments that need grading (teachers). Returns an error object with
    "error", "message", and optionally "status_code" keys on failure.
    """
    try:
        paginated = await canvas_api_client.get_rest_paginated(
            endpoint=REST_ENDPOINT, params={"per_page": 100}
        )
        items = [TodoItem.model_validate(item) for item in paginated.items]
        return list_result(items, truncated=paginated.truncated)

    except Exception as e:
        return as_tool_error(e, source="canvas_rest")


get_todo_items_tool: Final[Tool] = Tool.from_function(
    name="get_todo_items",
    description=(
        "List the current user's Canvas todo items: assignments that need "
        "submitting soon (students) or grading (teachers)."
    ),
    fn=get_todo_items,
)
