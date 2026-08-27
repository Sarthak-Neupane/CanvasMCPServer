"""Helpers for Canvas assignment rubric responses."""

from __future__ import annotations

from typing import Any, Dict, Optional

from ...models import Rubric, RubricCriterion


def rubric_from_assignment(assignment: Dict[str, Any]) -> Optional[Rubric]:
    """Build a Rubric from a Canvas assignment object with rubric included."""
    criteria_raw = assignment.get("rubric")
    if not isinstance(criteria_raw, list) or not criteria_raw:
        return None

    settings = assignment.get("rubric_settings")
    points_possible: Optional[float] = None
    if isinstance(settings, dict):
        raw_points = settings.get("points_possible")
        if raw_points is not None:
            points_possible = float(raw_points)

    criteria = [
        RubricCriterion.model_validate(row)
        for row in criteria_raw
        if isinstance(row, dict)
    ]
    if not criteria:
        return None

    assignment_id = assignment.get("id")
    return Rubric(
        assignment_id=int(assignment_id) if assignment_id is not None else None,
        points_possible=points_possible,
        use_rubric_for_grading=assignment.get("use_rubric_for_grading"),
        criteria=criteria,
        result_count=len(criteria),
    )
