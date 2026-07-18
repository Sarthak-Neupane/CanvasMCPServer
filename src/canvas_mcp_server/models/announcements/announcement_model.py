from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field


class AnnouncementAuthorRef(BaseModel):
    name: Annotated[
        Optional[str], Field(description="The name of the announcement author")
    ] = None


class Announcement(BaseModel):
    id: Annotated[
        str,
        Field(alias="_id", description="The numeric Canvas ID of the announcement"),
    ]
    title: Annotated[
        Optional[str],
        Field(description="The announcement title", examples=["Exam moved to Friday"]),
    ] = None
    message: Annotated[
        Optional[str],
        Field(description="The announcement body as HTML"),
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
