from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field


class UpcomingAssignment(BaseModel):
    """An upcoming assignment extracted from the user's upcoming events."""

    id: Annotated[
        Optional[int], Field(description="The numeric Canvas ID of the assignment")
    ] = None
    name: Annotated[
        Optional[str],
        Field(description="The assignment name", examples=["Problem Set 3"]),
    ] = None
    due_at: Annotated[
        Optional[datetime], Field(description="When the assignment is due")
    ] = None
    points_possible: Annotated[
        Optional[float], Field(description="Maximum points possible")
    ] = None
    course_id: Annotated[
        Optional[int], Field(description="The course the assignment belongs to")
    ] = None
    context_code: Annotated[
        Optional[str],
        Field(
            description="Canvas context code of the course",
            examples=["course_12942"],
        ),
    ] = None
    html_url: Annotated[
        Optional[str], Field(description="Link to the assignment in Canvas")
    ] = None
