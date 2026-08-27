"""Snippet helpers for course content search."""

from __future__ import annotations

import re

from ...utils.html import html_to_text

_SNIPPET_MAX_LEN = 200
_WINDOW = 80


def plain_text(value: str) -> str:
    """Normalize HTML or plain text for snippet extraction."""
    if "<" in value and ">" in value:
        return html_to_text(value)
    return re.sub(r"\s+", " ", value).strip()


def make_snippet(text: str, query: str, *, max_len: int = _SNIPPET_MAX_LEN) -> str:
    """Return a bounded excerpt around the first query match."""
    normalized = plain_text(text)
    if not normalized:
        return ""

    lowered = normalized.lower()
    query_lower = query.strip().lower()
    if not query_lower:
        return normalized[:max_len]

    # Prefer first matching token when the full phrase is absent.
    start = lowered.find(query_lower)
    if start < 0:
        for token in query_lower.split():
            start = lowered.find(token)
            if start >= 0:
                break

    if start < 0:
        return normalized[:max_len]

    window_start = max(0, start - _WINDOW)
    window_end = min(len(normalized), start + max_len)
    snippet = normalized[window_start:window_end].strip()
    if window_start > 0:
        snippet = "..." + snippet
    if window_end < len(normalized):
        snippet = snippet + "..."
    return snippet[: max_len + 3]
