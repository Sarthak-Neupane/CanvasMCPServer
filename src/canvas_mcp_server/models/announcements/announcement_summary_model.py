"""Summary model for announcement list responses (no HTML body)."""

from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field

from .announcement_model import AnnouncementAuthorRef


class AnnouncementSummary(BaseModel):
    """Announcement metadata for list tools — use get_discussion for full body."""

    id: Annotated[
        str,
        Field(alias="_id", description="The numeric Canvas ID of the announcement"),
    ]
    title: Annotated[
        Optional[str],
        Field(description="The announcement title", examples=["Exam moved to Friday"]),
    ] = None
    postedAt: Annotated[
        Optional[datetime],
        Field(description="When the announcement was posted"),
    ] = None
    contextName: Annotated[
        Optional[str],
        Field(description="The name of the course the announcement belongs to"),
    ] = None
    author: Annotated[
        Optional[AnnouncementAuthorRef],
        Field(description="The announcement author, if visible"),
    ] = None
    source_type: Annotated[
        Optional[str],
        Field(description="Canvas resource kind for provenance"),
    ] = None
    course_id: Annotated[
        Optional[str],
        Field(description="Owning course id"),
    ] = None
    resource_id: Annotated[
        Optional[str],
        Field(description="Announcement id"),
    ] = None
    canvas_url: Annotated[
        Optional[str],
        Field(description="Canvas web path for the announcement"),
    ] = None
