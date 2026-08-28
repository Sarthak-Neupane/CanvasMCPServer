"""Tests for ListResult wrapper."""

from canvas_mcp_server.models import ListResult, ResultStatus
from canvas_mcp_server.models.common.result_status import RESULT_STATUS_DESCRIPTIONS
from canvas_mcp_server.utils.list_results import list_result


def test_list_result_from_items() -> None:
    wrapped = list_result(["a", "b"], truncated=True)

    assert isinstance(wrapped, ListResult)
    assert wrapped.results == ["a", "b"]
    assert wrapped.result_count == 2
    assert wrapped.truncated is True


def test_list_result_empty() -> None:
    wrapped = list_result([], truncated=False)

    assert isinstance(wrapped, ListResult)
    assert wrapped.results == []
    assert wrapped.result_count == 0
    assert wrapped.truncated is False


def test_result_status_vocabulary() -> None:
    assert ResultStatus.OK == "ok"
    assert ResultStatus.EMPTY == "empty"
    assert ResultStatus.NOT_FOUND == "not_found"
    assert ResultStatus.NOT_APPLICABLE == "not_applicable"
    assert ResultStatus.PERMISSION_DENIED == "permission_denied"
    assert ResultStatus.LOCKED == "locked"
    assert ResultStatus.NOT_YET_AVAILABLE == "not_yet_available"
    assert ResultStatus.EXTERNAL_TOOL == "external_tool"
    assert ResultStatus.UNSUPPORTED_BY_CANVAS == "unsupported_by_canvas"
    assert ResultStatus.PARTIAL == "partial"
    assert len(RESULT_STATUS_DESCRIPTIONS) == len(ResultStatus)
