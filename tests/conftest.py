"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import pytest

from canvas_mcp_server.utils.canvas_api import canvas_api_client
from tests.helpers.canvas_mock import CanvasAPIMock


@pytest.fixture
def canvas_api() -> CanvasAPIMock:
    """
    Patch the global Canvas API client for one test.

    Register responses with canvas_api.rest_returns(...) or
    canvas_api.graphql_returns(...) before calling tool functions.
    """
    original_graphql = canvas_api_client.post_graphql_query
    original_rest = canvas_api_client.get_rest
    original_download = canvas_api_client.download_file_bytes
    mock = CanvasAPIMock().apply()
    yield mock
    canvas_api_client.post_graphql_query = original_graphql
    canvas_api_client.get_rest = original_rest
    canvas_api_client.download_file_bytes = original_download


@pytest.fixture
def download_dir(tmp_path, monkeypatch):
    """Point CANVAS_DOWNLOAD_DIR at a temp directory for download tests."""
    monkeypatch.setattr(
        "canvas_mcp_server.config.Config.CANVAS_DOWNLOAD_DIR",
        str(tmp_path),
    )
    return tmp_path
