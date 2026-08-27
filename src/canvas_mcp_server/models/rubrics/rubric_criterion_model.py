"""Pydantic models for Canvas rubric criteria."""

from typing import Annotated, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .rubric_rating_model import RubricRating


class RubricCriterion(BaseModel):
    """One row on a Canvas rubric."""

    model_config = ConfigDict(populate_by_name=True)

    criterion_id: Annotated[
        str,
        Field(alias="id", description="Canvas criterion id"),
    ]
    description: Annotated[
        Optional[str],
        Field(description="Criterion title or short label"),
    ] = None
    long_description: Annotated[
        Optional[str],
        Field(description="Detailed criterion description"),
    ] = None
    points: Annotated[
        Optional[float],
        Field(description="Maximum points for this criterion"),
    ] = None
    criterion_use_range: Annotated[
        Optional[bool],
        Field(description="Whether partial credit ranges are enabled"),
    ] = None
    ignore_for_scoring: Annotated[
        Optional[bool],
        Field(description="Whether this row is excluded from scoring"),
    ] = None
    ratings: Annotated[
        List[RubricRating],
        Field(
            default_factory=list,
            description="Rating levels for this criterion",
        ),
    ]
