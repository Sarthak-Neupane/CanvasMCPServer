"""Regression tests for download MCP tools."""

from __future__ import annotations

from pathlib import Path

import pytest

from canvas_mcp_server.models import DownloadBatchResult, DownloadedFile
from canvas_mcp_server.tools.downloads.download_assignment_files import (
    download_assignment_files,
)
from canvas_mcp_server.tools.downloads.download_course_files import download_course_files
from canvas_mcp_server.tools.downloads.download_file import download_file
from canvas_mcp_server.tools.downloads.download_module_files import download_module_files
from tests.fixtures.files import (
    ASSIGNMENT_WITH_FILE_EMBED_REST,
    COURSE_META_REST,
    FILE_BYTES,
    FILE_DETAIL_REST,
    FILE_LIST_REST,
)
from tests.fixtures.modules import MODULE_ITEMS_REST
from tests.helpers.assertions import assert_http_error
from tests.helpers.canvas_mock import CanvasAPIMock


def _setup_download_mocks(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns("v1/courses/100001", COURSE_META_REST)
    canvas_api.rest_returns("v1/files/500001", FILE_DETAIL_REST)
    canvas_api.download.return_value = FILE_BYTES


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


async def test_download_file_skip_if_exists(
    canvas_api: CanvasAPIMock,
    download_dir: Path,
) -> None:
    _setup_download_mocks(canvas_api)
    existing = download_dir / "Intro to Testing" / "verify-test" / "syllabus.pdf"
    existing.parent.mkdir(parents=True, exist_ok=True)
    existing.write_bytes(b"already here")

    result = await download_file("500001", "100001", folder="verify-test")

    assert isinstance(result, DownloadedFile)
    assert result.skipped is True
    assert result.bytes_written == 0
    assert existing.read_bytes() == b"already here"
    canvas_api.download.assert_not_called()


async def test_download_file_rejects_path_traversal(
    canvas_api: CanvasAPIMock,
    download_dir: Path,
) -> None:
    result = await download_file("500001", "100001", folder="../escape")

    assert isinstance(result, dict)
    assert result["error"] == "Invalid Argument"
    assert ".." in result["message"]


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


async def test_download_file_permission_error(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns("v1/courses/100001", COURSE_META_REST)
    canvas_api.rest_error("v1/files/500001", status_code=403, message="Forbidden")

    result = await download_file("500001", "100001")

    assert isinstance(result, dict)
    assert result["error"] == "Download Error"
    assert "Forbidden" in result["message"]


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
