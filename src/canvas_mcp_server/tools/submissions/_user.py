"""Helpers for resolving the authenticated Canvas user."""

from __future__ import annotations

from ...utils import canvas_api_client
from ...utils.token_cache import cached_fetch


async def current_user_id() -> str:
    """Return the numeric Canvas user id for the API token."""

    async def _fetch() -> str:
        response = await canvas_api_client.get_rest("v1/users/self")
        data = response.data
        if not isinstance(data, dict) or data.get("id") is None:
            raise Exception("Could not resolve the current Canvas user id")
        return str(data["id"])

    return await cached_fetch("user", "self_id", _fetch, ttl=900.0)
