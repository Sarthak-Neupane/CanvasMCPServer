from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Annotated
from enum import Enum
from datetime import datetime

from .course_term_model import Term
from .course_progress_model import CourseProgress
from .course_calendar_model import CalendarLink
from ...constants import DefaultView, WorkflowState


class CourseDetail(BaseModel):
    id: Annotated[
        str, Field(description="the unique identifier for the course", example=370663)
    ]
    name: Annotated[
        str,
        Field(description="the full name of the course", example="InstructureCon 2012"),
    ]
    courseCode: Annotated[
        str, Field(description="the course code", example="INSTCON12")
    ]
    state: Annotated[
        WorkflowState,
        Field(description="the current state of the course", example="available"),
    ]