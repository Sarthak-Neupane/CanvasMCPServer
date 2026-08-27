"""Tests for the in-process token cache."""

from canvas_mcp_server.utils.token_cache import TokenBoundedCache, cached_fetch, token_cache


def test_token_cache_expires_entries(monkeypatch) -> None:
    cache = TokenBoundedCache(default_ttl=1.0)
    now = {"value": 0.0}

    def fake_monotonic() -> float:
        return now["value"]

    monkeypatch.setattr("canvas_mcp_server.utils.token_cache.time.monotonic", fake_monotonic)
    cache.set("ns", "value", "key")
    assert cache.get("ns", "key") == "value"

    now["value"] = 2.0
    assert cache.get("ns", "key") is None


async def test_cached_fetch_reuses_value() -> None:
    token_cache.clear()
    calls = {"count": 0}

    async def fetch() -> str:
        calls["count"] += 1
        return "ok"

    first = await cached_fetch("test", "item", fetch)
    second = await cached_fetch("test", "item", fetch)

    assert first == "ok"
    assert second == "ok"
    assert calls["count"] == 1
