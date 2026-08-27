"""Regression tests for file listing MCP tools."""

from __future__ import annotations

import pytest

from canvas_mcp_server.models import FileDetail, FileSummary, FolderSummary
from canvas_mcp_server.tools.files.get_course_files import get_course_files
from canvas_mcp_server.tools.files.get_course_folders import get_course_folders
from canvas_mcp_server.tools.files.get_file_details import get_file_details
from canvas_mcp_server.tools.files.get_folder_files import get_folder_files
from tests.fixtures.files import FILE_DETAIL_REST, FILE_LIST_REST, FOLDER_LIST_REST
from tests.helpers.assertions import assert_http_error
from tests.helpers.canvas_mock import CanvasAPIMock


async def test_get_course_files_success(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns("v1/courses/100001/files", FILE_LIST_REST)

    result = await get_course_files("100001")

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], FileSummary)
    assert result[0].id == 500001
    assert result[0].display_name == "syllabus.pdf"
    assert result[0].content_type == "application/pdf"


async def test_get_course_files_search_term(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns("v1/courses/100001/files", FILE_LIST_REST)

    await get_course_files("100001", search_term="syllabus")

    assert canvas_api.get_rest_paginated_mock.await_args is not None
    assert (
        canvas_api.get_rest_paginated_mock.await_args.kwargs["params"]["search_term"]
        == "syllabus"
    )


async def test_get_course_files_follows_link_pages(canvas_api: CanvasAPIMock) -> None:
    page_two_item = {
        **FILE_LIST_REST[0],
        "id": 500002,
        "display_name": "notes.pdf",
        "filename": "notes.pdf",
    }
    canvas_api.rest_returns_pages(
        "v1/courses/100001/files",
        [FILE_LIST_REST, [page_two_item]],
    )

    result = await get_course_files("100001")

    assert isinstance(result, list)
    assert len(result) == 2
    assert {item.id for item in result} == {500001, 500002}


async def test_get_course_folders_success(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns("v1/courses/100001/folders", FOLDER_LIST_REST)

    result = await get_course_folders("100001")

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], FolderSummary)
    assert result[0].id == 600001
    assert result[0].name == "course files"
    assert result[0].files_count == 1


async def test_get_folder_files_success(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns("v1/folders/600001/files", FILE_LIST_REST)

    result = await get_folder_files("600001")

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].display_name == "syllabus.pdf"


async def test_get_file_details_content_type_alias(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns("v1/files/500001", FILE_DETAIL_REST)

    result = await get_file_details("500001")

    assert isinstance(result, FileDetail)
    assert result.content_type == "application/pdf"
    assert result.display_name == "syllabus.pdf"


@pytest.mark.parametrize(
    ("tool_fn", "args", "endpoint"),
    [
        (get_course_files, ("100001",), "v1/courses/100001/files"),
        (get_course_folders, ("100001",), "v1/courses/100001/folders"),
        (get_folder_files, ("600001",), "v1/folders/600001/files"),
        (get_file_details, ("500001",), "v1/files/500001"),
    ],
)
async def test_file_tools_permission_errors(
    canvas_api: CanvasAPIMock,
    tool_fn,
    args: tuple[str, ...],
    endpoint: str,
) -> None:
    canvas_api.rest_error(endpoint, status_code=403, message="Forbidden")

    result = await tool_fn(*args)

    assert_http_error(result, 403)
