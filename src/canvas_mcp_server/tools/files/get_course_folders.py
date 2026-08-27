"""Tool for listing folders in a Canvas course via the REST API.

Uses GET /api/v1/courses/:course_id/folders (flat list including subfolders).
"""

from typing import Final, List, Dict, Any, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import FolderSummary
from ...utils import canvas_api_client, HTTPError

CourseFoldersResponse: TypeAlias = Union[List[FolderSummary], Dict[str, Any]]


async def get_course_folders(
    course_id: Annotated[
        str,
        Field(description="The course ID (numeric Canvas ID, e.g. '182571')."),
    ],
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
        data = await canvas_api_client.get_rest_paginated(
            endpoint=f"v1/courses/{course_id}/folders",
            params={"per_page": 100},
        )
        return [FolderSummary.model_validate(item) for item in data]

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


get_course_folders_tool: Final[Tool] = Tool.from_function(
    name="get_course_folders",
    description=(
        "List all folders in a Canvas course (flat list with full paths and "
        "file counts). Use get_folder_files to list files in a folder."
    ),
    fn=get_course_folders,
)
