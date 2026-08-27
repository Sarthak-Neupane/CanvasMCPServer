"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import pytest

from canvas_mcp_server.config import Config
from canvas_mcp_server.utils.canvas_api import canvas_api_client
from canvas_mcp_server.utils.token_cache import token_cache
from tests.helpers.canvas_mock import CanvasAPIMock


@pytest.fixture(autouse=True)
def clear_token_cache() -> None:
    token_cache.clear()
    yield
    token_cache.clear()


@pytest.fixture
def canvas_api(monkeypatch) -> CanvasAPIMock:
    """
    Patch the global Canvas API client for one test.

    Register responses with canvas_api.rest_returns(...) or
    canvas_api.graphql_returns(...) before calling tool functions.
    """
    monkeypatch.setattr(
        Config,
        "CANVAS_BASE_URL",
        "https://canvas.example.edu/api",
    )
    monkeypatch.setattr(Config, "CANVAS_API_TOKEN", "test-token")
    original_graphql = canvas_api_client.post_graphql_query
    original_rest = canvas_api_client.get_rest
    original_get_rest_paginated = canvas_api_client.get_rest_paginated
    original_download_to_path = canvas_api_client.download_file_to_path
    mock = CanvasAPIMock().apply()
    yield mock
    canvas_api_client.post_graphql_query = original_graphql
    canvas_api_client.get_rest = original_rest
    canvas_api_client.get_rest_paginated = original_get_rest_paginated
    canvas_api_client.download_file_to_path = original_download_to_path


@pytest.fixture
def download_dir(tmp_path, monkeypatch):
    """Point CANVAS_DOWNLOAD_DIR at a temp directory for download tests."""
    monkeypatch.setattr(
        "canvas_mcp_server.config.Config.CANVAS_DOWNLOAD_DIR",
        str(tmp_path),
    )
    return tmp_path
