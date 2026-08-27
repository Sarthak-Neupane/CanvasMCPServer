"""Tool for listing files in a Canvas folder via the REST API.

Uses GET /api/v1/folders/:folder_id/files.
"""

from typing import Final, List, Dict, Any, Optional, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import FileSummary
from ...utils import canvas_api_client, HTTPError
from ._params import build_file_list_params

FolderFilesResponse: TypeAlias = Union[List[FileSummary], Dict[str, Any]]


async def get_folder_files(
    folder_id: Annotated[
        str,
        Field(
            description=(
                "The folder ID (numeric Canvas ID from get_course_folders)."
            ),
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
) -> FolderFilesResponse:
    """
    List files in a Canvas folder.

    Returns file metadata for files directly in the folder (not subfolders).
    Optional search_term and content_type narrow results.

    Returns an error object with "error", "message", and optionally
    "status_code" keys on failure.
    """
    try:
        response = await canvas_api_client.get_rest(
            endpoint=f"v1/folders/{folder_id}/files",
            params=build_file_list_params(search_term, content_type),
        )
        if not isinstance(response.data, list):
            raise Exception("Canvas folder files response was not a list")
        return [FileSummary.model_validate(item) for item in response.data]

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


get_folder_files_tool: Final[Tool] = Tool.from_function(
    name="get_folder_files",
    description=(
        "List files in a Canvas folder by folder_id. Returns metadata only "
        "(no download). Optional search_term and content_type filters."
    ),
    fn=get_folder_files,
)
