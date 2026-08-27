"""Discussion tool error helpers."""

from __future__ import annotations

from typing import Any, Dict, Optional

from ...utils.http_client import HTTPError


def discussion_http_error(e: HTTPError) -> Optional[Dict[str, Any]]:
    """Map Canvas discussion HTTP failures to student-friendly error objects."""
    if e.status_code == 403:
        body = e.response_data
        if body == "require_initial_post" or (
            isinstance(body, str) and "require_initial_post" in body
        ):
            return {
                "error": "Discussion Locked",
                "message": (
                    "You must post a reply before viewing other posts in this "
                    "discussion."
                ),
                "status_code": 403,
                "lock_reason": "require_initial_post",
            }
    if e.status_code == 503:
        return {
            "error": "Discussion Unavailable",
            "message": (
                "Canvas has not built the discussion view yet. Retry in a moment."
            ),
            "status_code": 503,
        }
    return None
