"""Bounded in-process TTL cache keyed by API token fingerprint."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, Optional, TypeVar, cast

from ..config import Config

T = TypeVar("T")

DEFAULT_CACHE_TTL_SECONDS = 300.0
DEFAULT_MAX_ENTRIES = 256


@dataclass
class _CacheEntry:
    value: Any
    expires_at: float


class TokenBoundedCache:
    """LRU-ish TTL cache scoped to the active Canvas API token."""

    def __init__(
        self,
        *,
        max_entries: int = DEFAULT_MAX_ENTRIES,
        default_ttl: float = DEFAULT_CACHE_TTL_SECONDS,
    ) -> None:
        self._max_entries = max_entries
        self._default_ttl = default_ttl
        self._store: Dict[tuple[str, ...], _CacheEntry] = {}

    def clear(self) -> None:
        """Drop all cached entries (used in tests)."""
        self._store.clear()

    def _token_fingerprint(self) -> str:
        token = Config.CANVAS_API_TOKEN or ""
        return hashlib.sha256(token.encode()).hexdigest()[:16]

    def _cache_key(self, namespace: str, *key_parts: str) -> tuple[str, ...]:
        return (self._token_fingerprint(), namespace, *key_parts)

    def _evict_expired(self, now: float) -> None:
        expired = [key for key, entry in self._store.items() if entry.expires_at <= now]
        for key in expired:
            del self._store[key]

    def _trim_size(self) -> None:
        if len(self._store) <= self._max_entries:
            return
        oldest = sorted(self._store.items(), key=lambda item: item[1].expires_at)
        for key, _entry in oldest[: len(self._store) - self._max_entries]:
            del self._store[key]

    def get(self, namespace: str, *key_parts: str) -> Optional[Any]:
        now = time.monotonic()
        self._evict_expired(now)
        entry = self._store.get(self._cache_key(namespace, *key_parts))
        if entry is None or entry.expires_at <= now:
            return None
        return entry.value

    def set(
        self,
        namespace: str,
        value: Any,
        *key_parts: str,
        ttl: Optional[float] = None,
    ) -> None:
        now = time.monotonic()
        self._evict_expired(now)
        key = self._cache_key(namespace, *key_parts)
        self._store[key] = _CacheEntry(
            value=value,
            expires_at=now + (ttl if ttl is not None else self._default_ttl),
        )
        self._trim_size()


token_cache = TokenBoundedCache()


async def cached_fetch(
    namespace: str,
    key: str,
    fetch: Callable[[], Awaitable[T]],
    *,
    ttl: Optional[float] = None,
) -> T:
    """Return a cached value or fetch and store it."""
    cached = token_cache.get(namespace, key)
    if cached is not None:
        return cast(T, cached)
    value = await fetch()
    token_cache.set(namespace, value, key, ttl=ttl)
    return value
