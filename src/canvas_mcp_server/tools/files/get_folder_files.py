"""Tool for listing files in a Canvas folder via the REST API.

Uses GET /api/v1/folders/:folder_id/files.
"""

from typing import Annotated, Any, Dict, Final, List, Optional, TypeAlias, Union

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...errors import as_tool_error
from ...models import FileSummary, ListResult
from ...utils import canvas_api_client
from ...utils.list_limits import (
    DEFAULT_LIST_LIMIT,
    ListLimitField,
    finalize_list,
    resolve_list_limit,
)
from ._params import build_file_list_params

FolderFilesResponse: TypeAlias = Union[ListResult[FileSummary], Dict[str, Any]]


async def get_folder_files(
    folder_id: Annotated[
        str,
        Field(
            description=("The folder ID (numeric Canvas ID from get_course_folders)."),
        ),
    ],
    search_term: Annotated[
        Optional[str],
        Field(
            description="Optional partial filename filter within the folder.",
        ),
    ] = None,
    content_type: Annotated[
        Optional[str],
        Field(
            description=(
                "Optional MIME type filter, e.g. 'application/pdf' or 'image'."
            ),
        ),
    ] = None,
    limit: ListLimitField = DEFAULT_LIST_LIMIT,
) -> FolderFilesResponse:
    """
    List files in a Canvas folder.

    Returns file metadata for files directly in the folder (not subfolders).
    Optional search_term and content_type narrow results.

    Returns an error object with "error", "message", and optionally
    "status_code" keys on failure.
    """
    try:
        paginated = await canvas_api_client.get_rest_paginated(
            endpoint=f"v1/folders/{folder_id}/files",
            params=build_file_list_params(search_term, content_type),
            max_items=resolve_list_limit(limit),
        )
        items = [FileSummary.model_validate(item) for item in paginated.items]
        return finalize_list(
            items, resolve_list_limit(limit), truncated=paginated.truncated
        )

    except Exception as e:
        return as_tool_error(e, source="canvas_rest")


get_folder_files_tool: Final[Tool] = Tool.from_function(
    name="get_folder_files",
    description=(
        "List files in a Canvas folder by folder_id. Returns metadata only "
        "(no download). Optional search_term and content_type filters."
    ),
    fn=get_folder_files,
)
