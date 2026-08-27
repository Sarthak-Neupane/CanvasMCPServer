"""Pydantic models for Canvas assignment rubrics."""

from typing import Annotated, List, Optional

from pydantic import BaseModel, Field

from .rubric_criterion_model import RubricCriterion


class Rubric(BaseModel):
    """Rubric attached to an assignment (criteria and ratings only)."""

    assignment_id: Annotated[
        Optional[int],
        Field(description="Assignment the rubric is attached to"),
    ] = None
    points_possible: Annotated[
        Optional[float],
        Field(description="Total rubric points when Canvas provides them"),
    ] = None
    use_rubric_for_grading: Annotated[
        Optional[bool],
        Field(
            description=(
                "Whether the rubric is used for grading vs advisory only"
            ),
        ),
    ] = None
    criteria: Annotated[
        List[RubricCriterion],
        Field(description="Rubric rows with rating levels"),
    ]
