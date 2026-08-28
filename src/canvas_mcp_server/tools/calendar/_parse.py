"""Helpers for Canvas calendar event responses."""

from __future__ import annotations

from typing import Any, Dict, Optional

from ...models import CalendarEvent


def course_id_from_context(context_code: Optional[str]) -> Optional[int]:
    """Extract a numeric course id from a Canvas context_code."""
    if not context_code or not context_code.startswith("course_"):
        return None
    suffix = context_code.split("_", 1)[1]
    try:
        return int(suffix)
    except ValueError:
        return None


def calendar_event_from_api(raw: Dict[str, Any], *, event_type: str) -> CalendarEvent:
    """Convert one Canvas calendar event JSON object to a CalendarEvent."""
    event_id = raw.get("id")
    context_code = raw.get("context_code")
    raw_assignment = raw.get("assignment")
    assignment: Dict[str, Any] = (
        raw_assignment if isinstance(raw_assignment, dict) else {}
    )

    all_day = raw.get("all_day")
    if all_day is None and assignment:
        all_day = assignment.get("all_day")

    all_day_date = raw.get("all_day_date")
    if not all_day_date and assignment:
        all_day_date = assignment.get("all_day_date")
    if all_day_date and "T" in str(all_day_date):
        all_day_date = str(all_day_date).split("T")[0]

    return CalendarEvent(
        id=str(event_id) if event_id is not None else "",
        event_type=event_type,
        title=raw.get("title"),
        start_at=raw.get("start_at") or assignment.get("due_at"),
        end_at=raw.get("end_at"),
        all_day=all_day,
        all_day_date=all_day_date,
        context_code=context_code,
        context_name=raw.get("context_name"),
        course_id=course_id_from_context(context_code),
        html_url=raw.get("html_url") or assignment.get("html_url"),
        location_name=raw.get("location_name"),
        workflow_state=raw.get("workflow_state"),
    )
