"""Shared helpers for Canvas dashboard cards."""

from __future__ import annotations

from typing import Set

from . import canvas_api_client
from .token_cache import cached_fetch

DASHBOARD_ENDPOINT = "v1/dashboard/dashboard_cards"


async def dashboard_course_ids() -> Set[str]:
    """Return course ids shown on the user's Canvas dashboard."""

    async def _fetch() -> Set[str]:
        response = await canvas_api_client.get_rest(DASHBOARD_ENDPOINT)
        cards = response.data
        if not isinstance(cards, list):
            raise Exception("Canvas dashboard_cards response was not a list")
        return {
            str(card["id"]) for card in cards if isinstance(card, dict) and "id" in card
        }

    return await cached_fetch("dashboard", "course_ids", _fetch)
