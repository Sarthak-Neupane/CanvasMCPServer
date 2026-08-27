"""Ranking helpers for course content search."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Optional, Set

from ._types import SearchDocument

_TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)


def _as_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        normalized = value.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(normalized)
        except ValueError:
            return None
    return None


def tokenize(text: str) -> Set[str]:
    """Lowercase alphanumeric tokens for overlap scoring."""
    return {match.group(0).lower() for match in _TOKEN_RE.finditer(text)}


def score_document(query: str, title: str, body: str = "") -> float:
    """
    Score a document against a query.

    Higher is better: exact title > substring title > token overlap >
    body matches > term frequency in body.
    """
    normalized_query = query.strip().lower()
    if not normalized_query:
        return 0.0

    title_lower = title.lower()
    body_lower = body.lower()
    query_tokens = tokenize(normalized_query)
    title_tokens = tokenize(title_lower)
    body_tokens = tokenize(body_lower)

    score = 0.0

    if title_lower == normalized_query:
        score += 100.0
    elif normalized_query in title_lower:
        score += 50.0

    title_overlap = len(query_tokens & title_tokens)
    score += title_overlap * 10.0

    if body_lower:
        if normalized_query in body_lower:
            score += 20.0
        body_overlap = len(query_tokens & body_tokens)
        score += body_overlap * 3.0
        for token in query_tokens:
            score += body_lower.count(token) * 0.5

    return score


def recency_boost(updated_at: Any) -> float:
    """Small tie-breaker favoring newer content (0.0–1.0)."""
    parsed = _as_datetime(updated_at)
    if parsed is None:
        return 0.0
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    age_days = (datetime.now(timezone.utc) - parsed).total_seconds() / 86400
    if age_days < 0:
        return 1.0
    return max(0.0, 1.0 - min(age_days, 365.0) / 365.0)


def rank_documents(
    query: str,
    documents: list[SearchDocument],
) -> list[tuple[SearchDocument, float]]:
    """Return documents with scores, highest first."""
    scored: list[tuple[SearchDocument, float]] = []
    for document in documents:
        base = score_document(query, document.title, document.body)
        if base <= 0:
            continue
        total = base + recency_boost(document.updated_at)
        scored.append((document, total))
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored
