"""Helpers for attaching untrusted-content provenance to tool responses."""

from __future__ import annotations

from typing import Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def build_canvas_web_path(
    source_type: str,
    course_id: str,
    resource_id: Optional[str] = None,
) -> Optional[str]:
    """Build a relative Canvas web path for a course resource."""
    if source_type == "syllabus":
        return f"/courses/{course_id}/assignments/syllabus"
    if not resource_id:
        return None
    path_by_type = {
        "page": f"/courses/{course_id}/pages/{resource_id}",
        "assignment": f"/courses/{course_id}/assignments/{resource_id}",
        "discussion": f"/courses/{course_id}/discussion_topics/{resource_id}",
        "announcement": f"/courses/{course_id}/discussion_topics/{resource_id}",
        "quiz": f"/courses/{course_id}/quizzes/{resource_id}",
        "file": f"/courses/{course_id}/files/{resource_id}",
        "module": f"/courses/{course_id}/modules/{resource_id}",
    }
    return path_by_type.get(source_type)


def attach_content_metadata(
    model: T,
    *,
    source_type: str,
    course_id: str,
    resource_id: Optional[str] = None,
    canvas_url: Optional[str] = None,
) -> T:
    """Attach provenance fields to a content-bearing response model."""
    resolved_url = canvas_url or build_canvas_web_path(
        source_type,
        course_id,
        resource_id,
    )
    return model.model_copy(
        update={
            "source_type": source_type,
            "course_id": str(course_id),
            "resource_id": str(resource_id) if resource_id is not None else None,
            "canvas_url": resolved_url,
        }
    )
