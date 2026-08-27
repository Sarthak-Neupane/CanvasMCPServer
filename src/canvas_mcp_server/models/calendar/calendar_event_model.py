"""Pydantic models for Canvas calendar events."""

from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field


class CalendarEvent(BaseModel):
    """One dated item from the Canvas calendar feed."""

    id: Annotated[
        str,
        Field(
            description=(
                "Canvas calendar event id (numeric string or "
                "assignment_{id} for assignment entries)"
            ),
        ),
    ]
    event_type: Annotated[
        str,
        Field(
            description="event, assignment, or sub_assignment",
            examples=["event"],
        ),
    ]
    title: Annotated[
        Optional[str],
        Field(description="Event or assignment title"),
    ] = None
    start_at: Annotated[
        Optional[datetime],
        Field(description="Start time (or due time for assignments)"),
    ] = None
    end_at: Annotated[
        Optional[datetime],
        Field(description="End time when Canvas provides one"),
    ] = None
    all_day: Annotated[
        Optional[bool],
        Field(description="True for all-day or midnight-due assignments"),
    ] = None
    all_day_date: Annotated[
        Optional[str],
        Field(description="Calendar date (yyyy-mm-dd) when all_day is true"),
    ] = None
    context_code: Annotated[
        Optional[str],
        Field(description="Owning calendar context, e.g. course_123"),
    ] = None
    context_name: Annotated[
        Optional[str],
        Field(description="Course or group name for the event"),
    ] = None
    course_id: Annotated[
        Optional[int],
        Field(description="Numeric course id parsed from context_code"),
    ] = None
    html_url: Annotated[
        Optional[str],
        Field(description="Canvas web URL to open the event or assignment"),
    ] = None
    location_name: Annotated[
        Optional[str],
        Field(description="Location for in-person calendar events"),
    ] = None
    workflow_state: Annotated[
        Optional[str],
        Field(description="active, published, locked, deleted, etc."),
    ] = None
