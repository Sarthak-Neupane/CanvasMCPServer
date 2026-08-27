"""Shared test assertions."""

from __future__ import annotations

from typing import Any, Dict


def assert_http_error(result: Any, status_code: int) -> Dict[str, Any]:
    assert isinstance(result, dict)
    assert result["error"] == "HTTP Error"
    assert isinstance(result["message"], str)
    assert result["status_code"] == status_code
    return result
