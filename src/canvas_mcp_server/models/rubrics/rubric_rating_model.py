"""Pydantic models for Canvas rubric ratings."""

from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field


class RubricRating(BaseModel):
    """One rating level for a rubric criterion."""

    model_config = ConfigDict(populate_by_name=True)

    rating_id: Annotated[
        str,
        Field(alias="id", description="Canvas rating id"),
    ]
    criterion_id: Annotated[
        Optional[str],
        Field(description="Parent criterion id when provided"),
    ] = None
    description: Annotated[
        Optional[str],
        Field(description="Short rating label"),
    ] = None
    long_description: Annotated[
        Optional[str],
        Field(description="Detailed rating description"),
    ] = None
    points: Annotated[
        Optional[float],
        Field(description="Points awarded for this rating"),
    ] = None
