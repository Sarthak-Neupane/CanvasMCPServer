"""Tests for ListResult wrapper."""

from canvas_mcp_server.models import ListResult
from canvas_mcp_server.utils.list_results import list_result


def test_list_result_from_items() -> None:
    wrapped = list_result(["a", "b"], truncated=True)

    assert isinstance(wrapped, ListResult)
    assert wrapped.results == ["a", "b"]
    assert wrapped.result_count == 2
    assert wrapped.truncated is True
