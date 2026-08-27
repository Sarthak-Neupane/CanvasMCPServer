"""Helpers for Canvas planner item responses."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from ...models import PlannerItem, PlannerSubmissionStatus

_PLANNABLE_TYPE_MAP = {
    "assignment": "assignment",
    "quiz": "quiz",
    "discussion_topic": "discussion",
    "wiki_page": "page",
    "planner_note": "note",
    "calendar_event": "calendar_event",
    "announcement": "announcement",
    "sub_assignment": "sub_assignment",
    "assessment_request": "assessment_request",
    "peer_review_sub_assignment": "peer_review",
}


def normalize_plannable_type(plannable_type: str) -> str:
    """Map Canvas plannable_type to a stable student-facing label."""
    key = plannable_type.strip().lower()
    return _PLANNABLE_TYPE_MAP.get(key, key or "unknown")


def _plannable_title(plannable: Dict[str, Any]) -> Optional[str]:
    title = plannable.get("title") or plannable.get("name")
    return str(title) if title is not None else None


def _plannable_datetime(
    plannable: Dict[str, Any],
    plannable_type: str,
) -> Optional[datetime]:
    if plannable_type == "planner_note":
        value = plannable.get("todo_date")
    else:
        value = plannable.get("due_at") or plannable.get("todo_date")
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    text = str(value)
    if text.endswith("Z"):
        text = text.replace("Z", "+00:00")
    return datetime.fromisoformat(text)


def planner_item_from_api(raw: Dict[str, Any]) -> PlannerItem:
    """Convert one Canvas planner item JSON object to a PlannerItem."""
    plannable_type = str(raw.get("plannable_type") or "")
    plannable = raw.get("plannable")
    if not isinstance(plannable, dict):
        plannable = {}

    override = raw.get("planner_override")
    marked_complete: Optional[bool] = None
    if isinstance(override, dict):
        marked_complete = override.get("marked_complete")

    submissions: Optional[PlannerSubmissionStatus] = None
    submissions_raw = raw.get("submissions")
    if isinstance(submissions_raw, dict):
        submissions = PlannerSubmissionStatus.model_validate(submissions_raw)

    plannable_id = raw.get("plannable_id")
    due_raw = _plannable_datetime(plannable, plannable_type)

    return PlannerItem(
        item_type=normalize_plannable_type(plannable_type),
        plannable_type=plannable_type or None,
        plannable_id=str(plannable_id) if plannable_id is not None else None,
        course_id=raw.get("course_id"),
        context_type=raw.get("context_type"),
        title=_plannable_title(plannable),
        due_at=due_raw,
        html_url=raw.get("html_url"),
        marked_complete=marked_complete,
        submissions=submissions,
    )
