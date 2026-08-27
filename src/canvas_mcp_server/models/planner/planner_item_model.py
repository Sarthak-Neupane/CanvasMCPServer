"""Pydantic models for Canvas planner items."""

from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field


class PlannerSubmissionStatus(BaseModel):
    """Submission flags for a planner item when Canvas provides them."""

    excused: Annotated[Optional[bool], Field()] = None
    graded: Annotated[Optional[bool], Field()] = None
    late: Annotated[Optional[bool], Field()] = None
    missing: Annotated[Optional[bool], Field()] = None
    needs_grading: Annotated[Optional[bool], Field()] = None
    with_feedback: Annotated[Optional[bool], Field()] = None


class PlannerItem(BaseModel):
    """One item from the student planner feed."""

    item_type: Annotated[
        str,
        Field(
            description=(
                "Normalized type: assignment, quiz, discussion, page, note, "
                "calendar_event, announcement, etc."
            ),
        ),
    ]
    plannable_type: Annotated[
        Optional[str],
        Field(description="Raw Canvas plannable_type value"),
    ] = None
    plannable_id: Annotated[
        Optional[str],
        Field(description="Canvas id of the underlying object"),
    ] = None
    course_id: Annotated[
        Optional[int],
        Field(description="Course id when the item belongs to a course"),
    ] = None
    context_type: Annotated[
        Optional[str],
        Field(description="Course or Group", examples=["Course"]),
    ] = None
    title: Annotated[
        Optional[str],
        Field(description="Display title from the plannable object"),
    ] = None
    due_at: Annotated[
        Optional[datetime],
        Field(
            description=(
                "Due or todo datetime for the item (timezone-aware when Canvas "
                "provides an offset or Z suffix)"
            ),
        ),
    ] = None
    html_url: Annotated[
        Optional[str],
        Field(description="Canvas web URL for the item"),
    ] = None
    marked_complete: Annotated[
        Optional[bool],
        Field(description="User-marked complete in the planner, if set"),
    ] = None
    submissions: Annotated[
        Optional[PlannerSubmissionStatus],
        Field(description="Submission status flags for the current user"),
    ] = None
