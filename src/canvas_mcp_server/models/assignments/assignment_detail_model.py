from datetime import datetime
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field

from .assignment_summary_model import AssignmentSummary


class AssignmentCourseRef(BaseModel):
    id: Annotated[
        Optional[str],
        Field(alias="_id", description="The numeric Canvas ID of the course"),
    ] = None
    name: Annotated[
        Optional[str],
        Field(description="The name of the course"),
    ] = None


class AssignmentDetail(AssignmentSummary):
    description: Annotated[
        Optional[str],
        Field(description="The assignment description as HTML"),
    ] = None
    unlockAt: Annotated[
        Optional[datetime],
        Field(description="The assignment is locked until this date"),
    ] = None
    lockAt: Annotated[
        Optional[datetime],
        Field(description="The assignment is locked after this date"),
    ] = None
    gradingType: Annotated[
        Optional[str],
        Field(
            description="How the assignment is graded",
            examples=["points"],
        ),
    ] = None
    submissionTypes: Annotated[
        Optional[List[str]],
        Field(
            description="Accepted submission types",
            examples=[["online_upload", "online_text_entry"]],
        ),
    ] = None
    allowedAttempts: Annotated[
        Optional[int],
        Field(description="Number of allowed submission attempts (null means unlimited)"),
    ] = None
    course: Annotated[
        Optional[AssignmentCourseRef],
        Field(description="The course this assignment belongs to"),
    ] = None
