"""Tool for listing folders in a Canvas course via the REST API.

Uses GET /api/v1/courses/:course_id/folders (flat list including subfolders).
"""

from typing import Annotated, Any, Dict, Final, List, TypeAlias, Union

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...errors import as_tool_error
from ...models import FolderSummary, ListResult
from ...utils import canvas_api_client
from ...utils.list_limits import (
    DEFAULT_LIST_LIMIT,
    ListLimitField,
    finalize_list,
    resolve_list_limit,
)

CourseFoldersResponse: TypeAlias = Union[ListResult[FolderSummary], Dict[str, Any]]


async def get_course_folders(
    course_id: Annotated[
        str,
        Field(description="The course ID (numeric Canvas ID, e.g. '182571')."),
    ],
    limit: ListLimitField = DEFAULT_LIST_LIMIT,
) -> CourseFoldersResponse:
    """
    List all folders in a Canvas course.

    Returns a flat list of every folder and subfolder with full_name paths,
    parent_folder_id, and file/subfolder counts. Use get_folder_files to list
    files inside a specific folder.

    Returns an error object with "error", "message", and optionally
    "status_code" keys on failure.
    """
    try:
        paginated = await canvas_api_client.get_rest_paginated(
            endpoint=f"v1/courses/{course_id}/folders",
            params={"per_page": 100},
            max_items=resolve_list_limit(limit),
        )
        items = [FolderSummary.model_validate(item) for item in paginated.items]
        return finalize_list(
            items, resolve_list_limit(limit), truncated=paginated.truncated
        )

    except Exception as e:
        return as_tool_error(e, source="canvas_rest")


get_course_folders_tool: Final[Tool] = Tool.from_function(
    name="get_course_folders",
    description=(
        "List all folders in a Canvas course (flat list with full paths and "
        "file counts). Use get_folder_files to list files in a folder."
    ),
    fn=get_course_folders,
)
