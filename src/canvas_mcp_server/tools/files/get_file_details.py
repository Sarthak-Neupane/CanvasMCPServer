"""Tool for fetching one Canvas file's metadata via the REST API.

Uses GET /api/v1/files/:file_id.
"""

from typing import Annotated, Any, Dict, Final, TypeAlias, Union

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...errors import as_tool_error
from ...models import FileDetail
from ...utils import canvas_api_client

FileDetailsResponse: TypeAlias = Union[FileDetail, Dict[str, Any]]


async def get_file_details(
    file_id: Annotated[
        str,
        Field(
            description=(
                "The file ID (numeric Canvas ID, e.g. from get_course_files "
                "or a module item content_id)."
            ),
        ),
    ],
) -> FileDetailsResponse:
    """
    Get metadata for a single Canvas file.

    Returns display name, MIME type, size, folder, authenticated download URL,
    lock info, and visibility. Does not download file contents.

    Returns an error object with "error", "message", and optionally
    "status_code" keys on failure.
    """
    try:
        response = await canvas_api_client.get_rest(
            endpoint=f"v1/files/{file_id}",
        )
        if not isinstance(response.data, dict):
            raise Exception("Canvas file response was not an object")
        return FileDetail.model_validate(response.data)

    except Exception as e:
        return as_tool_error(e, source="canvas_rest")


get_file_details_tool: Final[Tool] = Tool.from_function(
    name="get_file_details",
    description=(
        "Get metadata for one Canvas file: name, MIME type, size, folder, "
        "download URL, and lock info. Does not download the file."
    ),
    fn=get_file_details,
)
