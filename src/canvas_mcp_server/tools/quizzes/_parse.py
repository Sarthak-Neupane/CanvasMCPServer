"""Helpers for Canvas quiz REST responses."""

from __future__ import annotations

from typing import Any, Dict


def sanitize_quiz_api_payload(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Strip secrets and add student-safe flags before model validation."""
    data = dict(raw)
    access_code = data.pop("access_code", None)
    ip_filter = data.pop("ip_filter", None)
    data["requires_access_code"] = bool(access_code)
    data["has_ip_filter"] = bool(ip_filter)
    return data
