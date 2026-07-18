from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field


class TodoAssignmentRef(BaseModel):
    """Subset of the REST assignment object embedded in todo items."""

    id: Annotated[
        Optional[int], Field(description="The numeric Canvas ID of the assignment")
    ] = None
    name: Annotated[Optional[str], Field(description="The assignment name")] = None
    due_at: Annotated[
        Optional[datetime], Field(description="When the assignment is due")
    ] = None
    points_possible: Annotated[
        Optional[float], Field(description="Maximum points possible")
    ] = None
    html_url: Annotated[
        Optional[str], Field(description="Link to the assignment in Canvas")
    ] = None
    course_id: Annotated[
        Optional[int], Field(description="The course the assignment belongs to")
    ] = None


class TodoItem(BaseModel):
    type: Annotated[
        Optional[str],
        Field(
            description=(
                "'submitting' for an assignment that needs submitting soon, "
                "'grading' for an assignment that needs grading (teachers)"
            ),
            examples=["submitting"],
        ),
    ] = None
    assignment: Annotated[
        Optional[TodoAssignmentRef],
        Field(description="The assignment this todo item refers to"),
    ] = None
    context_type: Annotated[
        Optional[str],
        Field(description="'course' or 'group'", examples=["course"]),
    ] = None
    course_id: Annotated[
        Optional[int],
        Field(description="The course this todo item belongs to"),
    ] = None
    html_url: Annotated[
        Optional[str],
        Field(description="Link to the item in the Canvas web UI"),
    ] = None
    needs_grading_count: Annotated[
        Optional[int],
        Field(description="Number of submissions needing grading (grading items only)"),
    ] = None
