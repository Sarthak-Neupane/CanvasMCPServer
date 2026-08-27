"""Helpers for resolving the authenticated Canvas user."""

from __future__ import annotations

from ...utils import canvas_api_client


async def current_user_id() -> str:
    """Return the numeric Canvas user id for the API token."""
    response = await canvas_api_client.get_rest("v1/users/self")
    data = response.data
    if not isinstance(data, dict) or data.get("id") is None:
        raise Exception("Could not resolve the current Canvas user id")
    return str(data["id"])
