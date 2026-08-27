"""Helpers for parsing assignment description resources."""

from __future__ import annotations

from typing import List, Optional

from ...models import AssignmentResource, AssignmentResourceType
from ...utils.html import extract_canvas_resource_references


def parse_assignment_resources_from_html(
    html: Optional[str],
    *,
    default_course_id: Optional[str] = None,
) -> List[AssignmentResource]:
    """
    Parse and dedupe Canvas resources from assignment description HTML.

    Uses shared html utils for link and data-api-endpoint extraction.
    """
    references = extract_canvas_resource_references(html)
    resources: List[AssignmentResource] = []
    seen: set[tuple[str, str, str]] = set()

    for reference in references:
        resource_type = reference.get("type")
        if not resource_type:
            continue
        resource_id = reference.get("id")
        course_id = reference.get("course_id") or default_course_id
        if resource_id:
            key = (str(resource_type), str(resource_id), str(course_id or ""))
        else:
            key = (str(resource_type), str(reference.get("url") or ""), "")
        if key in seen:
            continue
        seen.add(key)

        resources.append(
            AssignmentResource(
                type=AssignmentResourceType(resource_type),
                id=resource_id,
                course_id=course_id,
                url=str(reference.get("url") or ""),
                label=reference.get("label"),
            )
        )

    return resources
