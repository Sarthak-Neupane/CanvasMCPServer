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

    return CalendarEvent(
        id=str(event_id) if event_id is not None else "",
        event_type=event_type,
        title=raw.get("title"),
        start_at=raw.get("start_at"),
        end_at=raw.get("end_at"),
        all_day=raw.get("all_day"),
        all_day_date=raw.get("all_day_date"),
        context_code=context_code,
        context_name=raw.get("context_name"),
        course_id=course_id_from_context(context_code),
        html_url=raw.get("html_url"),
        location_name=raw.get("location_name"),
        workflow_state=raw.get("workflow_state"),
    )
