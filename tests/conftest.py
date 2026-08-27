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
