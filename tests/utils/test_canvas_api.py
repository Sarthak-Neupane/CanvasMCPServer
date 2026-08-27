"""Tests for Canvas API client download behavior."""

import httpx
import pytest
import respx

from canvas_mcp_server.config import Config
from canvas_mcp_server.utils.canvas_api import canvas_api_client
from canvas_mcp_server.utils.http_client import HTTPError
from tests.fixtures.files import FILE_BYTES


@pytest.fixture
def canvas_download_config(monkeypatch) -> None:
    monkeypatch.setattr(Config, "CANVAS_API_TOKEN", "test-token")
    monkeypatch.setattr(Config, "CANVAS_BASE_URL", "https://canvas.example.edu/api")


@respx.mock
async def test_download_file_bytes_success(canvas_download_config) -> None:
    url = "https://canvas.example.edu/files/500001/download"
    respx.get(url).mock(return_value=httpx.Response(200, content=FILE_BYTES))

    content = await canvas_api_client.download_file_bytes(url)

    assert content == FILE_BYTES
    request = respx.calls.last.request
    assert request.headers["Authorization"] == "Bearer test-token"
    assert "content-type" not in {k.lower() for k in request.headers.keys()}


@respx.mock
async def test_download_file_bytes_http_error(canvas_download_config) -> None:
    url = "https://canvas.example.edu/files/500001/download"
    respx.get(url).mock(return_value=httpx.Response(403, text="Forbidden"))

    with pytest.raises(HTTPError, match="HTTP 403 error"):
        await canvas_api_client.download_file_bytes(url)


@respx.mock
async def test_download_file_to_path_streams_to_disk(
    canvas_download_config,
    tmp_path,
) -> None:
    url = "https://canvas.example.edu/files/500001/download"
    respx.get(url).mock(return_value=httpx.Response(200, content=FILE_BYTES))
    destination = tmp_path / "nested" / "syllabus.pdf"

    bytes_written = await canvas_api_client.download_file_to_path(url, destination)

    assert bytes_written == len(FILE_BYTES)
    assert destination.read_bytes() == FILE_BYTES


@respx.mock
async def test_download_file_to_path_rejects_content_length_over_limit(
    canvas_download_config,
    tmp_path,
) -> None:
    url = "https://canvas.example.edu/files/500001/download"
    respx.get(url).mock(
        return_value=httpx.Response(
            200,
            content=FILE_BYTES,
            headers={"content-length": str(len(FILE_BYTES))},
        )
    )
    destination = tmp_path / "syllabus.pdf"

    with pytest.raises(HTTPError, match="exceeds maximum download size"):
        await canvas_api_client.download_file_to_path(
            url,
            destination,
            max_bytes=len(FILE_BYTES) - 1,
        )

    assert not destination.exists()
