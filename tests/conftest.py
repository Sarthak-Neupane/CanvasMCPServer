"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import pytest

from tests.helpers.canvas_mock import CanvasAPIMock


@pytest.fixture
def canvas_api() -> CanvasAPIMock:
    """
    Patch the global Canvas API client for one test.

    Register responses with canvas_api.rest_returns(...) or
    canvas_api.graphql_returns(...) before calling tool functions.
    """
    mock = CanvasAPIMock().apply()
    yield mock
    # Restore is not required: each test gets fresh AsyncMocks via apply().


@pytest.fixture
def download_dir(tmp_path, monkeypatch):
    """Point CANVAS_DOWNLOAD_DIR at a temp directory for download tests."""
    monkeypatch.setattr(
        "canvas_mcp_server.config.Config.CANVAS_DOWNLOAD_DIR",
        str(tmp_path),
    )
    return tmp_path
