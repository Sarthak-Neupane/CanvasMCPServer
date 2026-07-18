"""Tool for listing the current user's todo items via the Canvas REST API.

The GraphQL schema does not expose todo items, so this tool uses the REST
endpoint GET /api/v1/users/self/todo.
"""

from typing import Final, List, Dict, Any, Union, TypeAlias

from mcp.server.fastmcp.tools import Tool

from ...models import TodoItem
from ...utils import canvas_api_client, HTTPError

TodoItemsResponse: TypeAlias = Union[List[TodoItem], Dict[str, Any]]

REST_ENDPOINT = "v1/users/self/todo"


async def get_todo_items() -> TodoItemsResponse:
    """
    List the current user's Canvas todo items.

    Items are either assignments that need submitting soon (students) or
    assignments that need grading (teachers). Returns an error object with
    "error", "message", and optionally "status_code" keys on failure.
    """
    try:
        response = await canvas_api_client.get_rest(
            endpoint=REST_ENDPOINT, params={"per_page": 100}
        )
        if not isinstance(response.data, list):
            raise Exception("Canvas todo response was not a list")
        return [TodoItem.model_validate(item) for item in response.data]

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


get_todo_items_tool: Final[Tool] = Tool.from_function(
    name="get_todo_items",
    description=(
        "List the current user's Canvas todo items: assignments that need "
        "submitting soon (students) or grading (teachers)."
    ),
    fn=get_todo_items,
)
