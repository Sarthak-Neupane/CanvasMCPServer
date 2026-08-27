"""Tests for Canvas API client download behavior."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest
import respx

from canvas_mcp_server.config import Config
from canvas_mcp_server.utils.canvas_api import CanvasAPIClient, canvas_api_client
from canvas_mcp_server.utils.http_client import HTTPError
from tests.fixtures.files import FILE_BYTES


@pytest.fixture
def canvas_download_config(monkeypatch) -> None:
    monkeypatch.setattr(Config, "CANVAS_API_TOKEN", "test-token")
    monkeypatch.setattr(Config, "CANVAS_BASE_URL", "https://canvas.example.edu/api")
    canvas_api_client.base_url = "https://canvas.example.edu/api"


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


@respx.mock
async def test_canvas_api_client_lifecycle(canvas_download_config) -> None:
    client = CanvasAPIClient()
    client.base_url = "https://canvas.example.edu/api"

    await client.start()
    shared = client._http_client
    assert shared is not None

    await client.start()
    assert client._http_client is shared

    await client.aclose()
    assert client._http_client is None


@respx.mock
async def test_get_rest_paginated_follows_link_header(
    canvas_download_config,
) -> None:
    page_one_url = (
        "https://canvas.example.edu/api/v1/courses/1/files?per_page=1"
    )
    page_two_url = (
        "https://canvas.example.edu/api/v1/courses/1/files?per_page=1&page=2"
    )
    link_header = f'<{page_two_url}>; rel="next"'

    respx.get(page_one_url).mock(
        return_value=httpx.Response(
            200,
            json=[{"id": 1, "display_name": "a.pdf"}],
            headers={"Link": link_header},
        )
    )
    respx.get(page_two_url).mock(
        return_value=httpx.Response(
            200,
            json=[{"id": 2, "display_name": "b.pdf"}],
        )
    )

    items = await canvas_api_client.get_rest_paginated(
        "v1/courses/1/files",
        params={"per_page": 1},
        max_pages=2,
    )

    assert len(items) == 2
    assert items[0]["id"] == 1
    assert items[1]["id"] == 2


@respx.mock
async def test_get_rest_retries_on_429(canvas_download_config, monkeypatch) -> None:
    monkeypatch.setattr(Config, "CANVAS_MAX_RETRIES", 2)
    monkeypatch.setattr(Config, "CANVAS_RETRY_BASE_DELAY", 0.01)
    url = "https://canvas.example.edu/api/v1/users/self/profile"
    route = respx.get(url).mock(
        side_effect=[
            httpx.Response(429, headers={"Retry-After": "0"}),
            httpx.Response(200, json={"id": 1, "name": "Student"}),
        ]
    )

    with patch(
        "canvas_mcp_server.utils.http_client.sleep_before_retry",
        new_callable=AsyncMock,
    ):
        response = await canvas_api_client.get_rest("v1/users/self/profile")

    assert response.data["id"] == 1
    assert route.call_count == 2


@respx.mock
async def test_get_rest_does_not_retry_on_403(canvas_download_config) -> None:
    url = "https://canvas.example.edu/api/v1/users/self/profile"
    route = respx.get(url).mock(return_value=httpx.Response(403, text="Forbidden"))

    with pytest.raises(HTTPError, match="access forbidden"):
        await canvas_api_client.get_rest("v1/users/self/profile")

    assert route.call_count == 1


@respx.mock
async def test_get_rest_retries_network_error(
    canvas_download_config,
    monkeypatch,
) -> None:
    monkeypatch.setattr(Config, "CANVAS_MAX_RETRIES", 2)
    monkeypatch.setattr(Config, "CANVAS_RETRY_BASE_DELAY", 0.01)
    url = "https://canvas.example.edu/api/v1/users/self/profile"
    call_count = 0

    def flaky_response(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise httpx.ConnectError("connection reset")
        return httpx.Response(200, json={"id": 1})

    route = respx.get(url).mock(side_effect=flaky_response)

    with patch(
        "canvas_mcp_server.utils.http_client.sleep_before_retry",
        new_callable=AsyncMock,
    ):
        response = await canvas_api_client.get_rest("v1/users/self/profile")

    assert response.data["id"] == 1
    assert route.call_count == 2


@respx.mock
async def test_download_file_bytes_retries_on_503(
    canvas_download_config,
    monkeypatch,
) -> None:
    monkeypatch.setattr(Config, "CANVAS_MAX_RETRIES", 2)
    monkeypatch.setattr(Config, "CANVAS_RETRY_BASE_DELAY", 0.01)
    url = "https://canvas.example.edu/files/500001/download"
    route = respx.get(url).mock(
        side_effect=[
            httpx.Response(503, text="Unavailable"),
            httpx.Response(200, content=FILE_BYTES),
        ]
    )

    with patch(
        "canvas_mcp_server.utils.retry_policy.sleep_before_retry",
        new_callable=AsyncMock,
    ):
        content = await canvas_api_client.download_file_bytes(url)

    assert content == FILE_BYTES
    assert route.call_count == 2
