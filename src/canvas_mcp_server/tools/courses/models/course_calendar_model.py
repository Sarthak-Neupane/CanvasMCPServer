from typing import Annotated
from pydantic import BaseModel, Field

class CalendarLink(BaseModel):
    ics: Annotated[
        str,
        Field(
            description="The URL of the calendar in ICS format",
            example="https://canvas.instructure.com/feeds/calendars/course_abcdef.ics",
        ),
    ]
