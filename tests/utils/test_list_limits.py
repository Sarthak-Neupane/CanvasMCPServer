"""Tests for list limit helpers."""

from canvas_mcp_server.utils.list_limits import (
    cap_items,
    finalize_list,
    resolve_list_limit,
)


def test_resolve_list_limit_clamps_range() -> None:
    assert resolve_list_limit(1) == 1
    assert resolve_list_limit(50) == 50
    assert resolve_list_limit(100) == 100
    assert resolve_list_limit(500) == 100


def test_cap_items_marks_truncation() -> None:
    capped, truncated = cap_items([1, 2, 3, 4], 2)

    assert capped == [1, 2]
    assert truncated is True


def test_finalize_list_wraps_list_result() -> None:
    result = finalize_list(["a", "b"], 10, truncated=False)

    assert result.result_count == 2
    assert result.truncated is False
