"""Tool for listing files in a Canvas course via the REST API.

Uses GET /api/v1/courses/:course_id/files.
"""

from typing import Final, List, Dict, Any, Optional, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...models import FileSummary, ListResult
from ...utils.list_results import list_result
from ...errors import as_tool_error
from ...utils import canvas_api_client
from ._params import build_file_list_params

CourseFilesResponse: TypeAlias = Union[ListResult[FileSummary], Dict[str, Any]]


async def get_course_files(
    course_id: Annotated[
        str,
        Field(description="The course ID (numeric Canvas ID, e.g. '182571')."),
    ],
    search_term: Annotated[
        Optional[str],
        Field(
            description=(
                "Optional partial filename filter, e.g. 'formula' or 'syllabus'."
            ),
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
) -> CourseFilesResponse:
    """
    List files in a Canvas course.

    Returns file metadata (id, display name, MIME type, size, folder, download
    URL). Does not download file contents. Optional search_term and
    content_type narrow results.

    Returns an error object with "error", "message", and optionally
    "status_code" keys on failure.
    """
    try:
        paginated = await canvas_api_client.get_rest_paginated(
            endpoint=f"v1/courses/{course_id}/files",
            params=build_file_list_params(search_term, content_type),
        )
        items = [FileSummary.model_validate(item) for item in paginated.items]
        return list_result(items, truncated=paginated.truncated)

    except Exception as e:
        return as_tool_error(e, source="canvas_rest")


get_course_files_tool: Final[Tool] = Tool.from_function(
    name="get_course_files",
    description=(
        "List files in a Canvas course with metadata (id, name, MIME type, "
        "size, download URL). Does not download files. Optional search_term "
        "and content_type filters, e.g. search_term='formula'."
    ),
    fn=get_course_files,
)
