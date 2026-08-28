"""Regression tests for download MCP tools."""

from __future__ import annotations

from pathlib import Path

import pytest

from canvas_mcp_server.errors import ErrorCode
from canvas_mcp_server.models import DownloadBatchResult, DownloadedFile
from canvas_mcp_server.tools.downloads.download_assignment_files import (
    download_assignment_files,
)
from canvas_mcp_server.tools.downloads.download_course_files import (
    download_course_files,
)
from canvas_mcp_server.tools.downloads.download_file import download_file
from canvas_mcp_server.tools.downloads.download_module_files import (
    download_module_files,
)
from tests.fixtures.assignments import ASSIGNMENT_REST_WITH_EMBEDS
from tests.fixtures.files import (
    ASSIGNMENT_WITH_FILE_EMBED_REST,
    COURSE_META_REST,
    FILE_BYTES,
    FILE_DETAIL_REST,
    FILE_LIST_REST,
)
from tests.fixtures.modules import MODULE_ITEMS_REST
from tests.helpers.assertions import assert_http_error, assert_tool_error
from tests.helpers.canvas_mock import CanvasAPIMock


def _setup_download_mocks(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns("v1/courses/100001", COURSE_META_REST)
    canvas_api.rest_returns("v1/files/500001", FILE_DETAIL_REST)


async def test_download_file_writes_to_temp_dir(
    canvas_api: CanvasAPIMock,
    download_dir: Path,
) -> None:
    _setup_download_mocks(canvas_api)

    result = await download_file("500001", "100001", folder="verify-test")

    assert isinstance(result, DownloadedFile)
    assert result.skipped is False
    assert result.bytes_written == len(FILE_BYTES)
    local_path = Path(result.local_path)
    assert local_path.exists()
    assert local_path.read_bytes() == FILE_BYTES
    assert local_path.is_relative_to(download_dir)


async def test_download_file_uses_collision_suffix(
    canvas_api: CanvasAPIMock,
    download_dir: Path,
) -> None:
    _setup_download_mocks(canvas_api)
    existing = download_dir / "Intro to Testing" / "verify-test" / "syllabus.pdf"
    existing.parent.mkdir(parents=True, exist_ok=True)
    existing.write_bytes(b"already here")

    result = await download_file("500001", "100001", folder="verify-test")

    assert isinstance(result, DownloadedFile)
    assert result.skipped is False
    assert result.bytes_written == len(FILE_BYTES)
    assert existing.read_bytes() == b"already here"
    collision_path = existing.parent / "syllabus (1).pdf"
    assert collision_path.exists()
    assert collision_path.read_bytes() == FILE_BYTES
    assert result.local_path == str(collision_path.resolve())


async def test_download_file_rejects_path_traversal(
    canvas_api: CanvasAPIMock,
    download_dir: Path,
) -> None:
    result = await download_file("500001", "100001", folder="../escape")

    assert_tool_error(
        result,
        ErrorCode.INVALID_ARGUMENT,
        title="Invalid Argument",
        message_contains="..",
    )


async def test_download_course_files_batch(
    canvas_api: CanvasAPIMock,
    download_dir: Path,
) -> None:
    _setup_download_mocks(canvas_api)
    canvas_api.rest_returns("v1/courses/100001/files", FILE_LIST_REST)

    result = await download_course_files("100001", folder="batch")

    assert isinstance(result, DownloadBatchResult)
    assert len(result.downloaded) == 1
    assert len(result.failed) == 0
    assert result.downloaded[0].skipped is False
    assert Path(result.downloaded[0].local_path).exists()


async def test_download_module_files_file_items_only(
    canvas_api: CanvasAPIMock,
    download_dir: Path,
) -> None:
    _setup_download_mocks(canvas_api)
    canvas_api.rest_returns(
        "v1/courses/100001/modules/300001/items",
        MODULE_ITEMS_REST,
    )

    result = await download_module_files("100001", "300001", folder="module")

    assert isinstance(result, DownloadBatchResult)
    assert len(result.downloaded) == 1
    assert result.downloaded[0].file_id == "500001"
    assert len(result.failed) == 0


async def test_download_assignment_files_html_id_extraction(
    canvas_api: CanvasAPIMock,
    download_dir: Path,
) -> None:
    _setup_download_mocks(canvas_api)
    canvas_api.rest_returns(
        "v1/courses/100001/assignments/200001",
        ASSIGNMENT_WITH_FILE_EMBED_REST,
    )

    result = await download_assignment_files("100001", "200001", folder="homework")

    assert isinstance(result, DownloadBatchResult)
    assert len(result.downloaded) == 1
    assert result.downloaded[0].file_id == "500001"
    assert Path(result.downloaded[0].local_path).exists()


async def test_download_assignment_files_ignores_non_file_resources(
    canvas_api: CanvasAPIMock,
    download_dir: Path,
) -> None:
    _setup_download_mocks(canvas_api)
    canvas_api.rest_returns(
        "v1/courses/100001/assignments/200001",
        ASSIGNMENT_REST_WITH_EMBEDS,
    )

    result = await download_assignment_files("100001", "200001", folder="homework")

    assert isinstance(result, DownloadBatchResult)
    assert len(result.downloaded) == 1
    assert result.downloaded[0].file_id == "500001"
    assert len(result.failed) == 0


async def test_download_assignment_files_empty_description(
    canvas_api: CanvasAPIMock,
    download_dir: Path,
) -> None:
    _setup_download_mocks(canvas_api)
    canvas_api.rest_returns(
        "v1/courses/100001/assignments/200001",
        {"id": 200001, "name": "No links", "description": "<p>Nothing here</p>"},
    )

    result = await download_assignment_files("100001", "200001")

    assert isinstance(result, DownloadBatchResult)
    assert result.downloaded == []
    assert result.failed == []
    canvas_api.download_to_path.assert_not_called()


async def test_download_assignment_files_assignment_not_found(
    canvas_api: CanvasAPIMock,
) -> None:
    canvas_api.rest_error(
        "v1/courses/100001/assignments/999999",
        status_code=404,
        message="Not found",
    )

    result = await download_assignment_files("100001", "999999")

    assert_http_error(result, 404)


async def test_download_file_permission_error(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns("v1/courses/100001", COURSE_META_REST)
    canvas_api.rest_error("v1/files/500001", status_code=403, message="Forbidden")

    result = await download_file("500001", "100001")

    assert_tool_error(
        result,
        ErrorCode.DOWNLOAD_FAILED,
        title="Download Error",
        message_contains="Forbidden",
    )


async def test_download_course_files_list_permission_error(
    canvas_api: CanvasAPIMock,
) -> None:
    canvas_api.rest_error(
        "v1/courses/100001/files",
        status_code=403,
        message="Forbidden",
    )

    result = await download_course_files("100001")

    assert_http_error(result, 403)


async def test_download_course_files_partial_failure(
    canvas_api: CanvasAPIMock,
    download_dir: Path,
) -> None:
    canvas_api.rest_returns("v1/courses/100001", COURSE_META_REST)
    canvas_api.rest_returns(
        "v1/courses/100001/files",
        [
            FILE_LIST_REST[0],
            {
                **FILE_LIST_REST[0],
                "id": 500002,
                "display_name": "notes.pdf",
                "filename": "notes.pdf",
                "url": "https://canvas.example.edu/files/500002/download",
            },
        ],
    )
    canvas_api.rest_returns("v1/files/500001", FILE_DETAIL_REST)
    canvas_api.rest_returns(
        "v1/files/500002",
        {
            **FILE_DETAIL_REST,
            "id": 500002,
            "display_name": "notes.pdf",
            "filename": "notes.pdf",
            "url": "https://canvas.example.edu/files/500002/download",
        },
    )

    async def _fail_second_download(
        url: str,
        destination: Path,
        *,
        max_bytes: int | None = None,
        timeout: float | None = None,
    ) -> int:
        del max_bytes, timeout
        if "500002" in url:
            from canvas_mcp_server.utils.http_client import HTTPError

            raise HTTPError("Forbidden", status_code=403, url=url)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(FILE_BYTES)
        return len(FILE_BYTES)

    canvas_api.download_to_path.side_effect = _fail_second_download

    result = await download_course_files("100001", folder="batch")

    assert isinstance(result, DownloadBatchResult)
    assert result.status == "completed_with_failures"
    assert result.matched_count == 2
    assert result.downloaded_count == 1
    assert result.failed_count == 1
    assert len(result.downloaded) == 1
    assert result.downloaded[0].file_id == "500001"
    assert len(result.failed) == 1
    assert result.failed[0].file_id == "500002"
    assert "Forbidden" in result.failed[0].message


async def test_download_file_course_mismatch(
    canvas_api: CanvasAPIMock,
    download_dir: Path,
) -> None:
    canvas_api.rest_returns("v1/courses/100002", {"id": 100002, "name": "French 101"})
    # File belongs to course 100001 (Physics), but caller asked for course 100002 (French)
    file_detail = {
        **FILE_DETAIL_REST,
        "context_type": "Course",
        "context_id": 100001,
    }
    canvas_api.rest_returns("v1/files/500001", file_detail)

    result = await download_file("500001", "100002", folder="verify")

    assert_tool_error(
        result,
        ErrorCode.RESOURCE_COURSE_MISMATCH,
        title="Resource Course Mismatch",
        message_contains="belongs to course 100001",
    )
    # Ensure no file was written to disk
    assert not (download_dir / "French 101").exists()


async def test_download_course_files_nothing_found(
    canvas_api: CanvasAPIMock,
) -> None:
    canvas_api.rest_returns("v1/courses/100001", COURSE_META_REST)
    canvas_api.rest_returns("v1/courses/100001/files", [])

    result = await download_course_files("100001")

    assert isinstance(result, DownloadBatchResult)
    assert result.status == "nothing_found"
    assert result.matched_count == 0
    assert result.downloaded_count == 0
    assert result.failed_count == 0
    assert result.skipped_count == 0
    assert result.downloaded == []
    assert result.failed == []
