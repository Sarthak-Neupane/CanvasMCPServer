"""Shared status vocabulary for Canvas MCP tool responses."""

from enum import StrEnum
from typing import Final


class ResultStatus(StrEnum):
    """Canonical status outcomes across Canvas MCP tool responses."""

    OK = "ok"
    EMPTY = "empty"
    NOT_FOUND = "not_found"
    NOT_APPLICABLE = "not_applicable"
    PERMISSION_DENIED = "permission_denied"
    LOCKED = "locked"
    NOT_YET_AVAILABLE = "not_yet_available"
    EXTERNAL_TOOL = "external_tool"
    UNSUPPORTED_BY_CANVAS = "unsupported_by_canvas"
    PARTIAL = "partial"


RESULT_STATUS_DESCRIPTIONS: Final[dict[ResultStatus, str]] = {
    ResultStatus.OK: "Request completed with matching results.",
    ResultStatus.EMPTY: "Request completed successfully but found zero matching items.",
    ResultStatus.NOT_FOUND: "The requested resource does not exist or is not visible.",
    ResultStatus.NOT_APPLICABLE: "The requested attribute/feature is not applicable to this resource (e.g. assignment has no rubric).",
    ResultStatus.PERMISSION_DENIED: "Canvas denied access to list this resource category.",
    ResultStatus.LOCKED: "The resource or module is locked (e.g. lock_at in future or prerequisite unmet).",
    ResultStatus.NOT_YET_AVAILABLE: "The resource is scheduled to unlock at a future date.",
    ResultStatus.EXTERNAL_TOOL: "Content is hosted by an external LTI tool (e.g. WebAssign, MindTap) and not stored in Canvas.",
    ResultStatus.UNSUPPORTED_BY_CANVAS: "The requested Canvas feature is disabled or not supported for this course.",
    ResultStatus.PARTIAL: "Batch or multi-resource request partially completed.",
}
