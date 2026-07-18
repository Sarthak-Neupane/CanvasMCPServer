from datetime import datetime
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field


class SubmissionUserRef(BaseModel):
    id: Annotated[
        Optional[str],
        Field(alias="_id", description="The numeric Canvas ID of the user"),
    ] = None
    name: Annotated[Optional[str], Field(description="The user's name")] = None


class SubmissionStatus(BaseModel):
    id: Annotated[
        str,
        Field(alias="_id", description="The numeric Canvas ID of the submission"),
    ]
    state: Annotated[
        Optional[str],
        Field(
            description="Workflow state of the submission",
            examples=["submitted"],
        ),
    ] = None
    submissionStatus: Annotated[
        Optional[str],
        Field(
            description="Human-oriented status, e.g. 'submitted', 'unsubmitted', 'late'",
        ),
    ] = None
    gradingStatus: Annotated[
        Optional[str],
        Field(
            description="Grading progress, e.g. 'graded', 'needs_grading', 'excused'",
        ),
    ] = None
    score: Annotated[
        Optional[float],
        Field(description="The raw score, if graded and visible"),
    ] = None
    grade: Annotated[
        Optional[str],
        Field(description="The translated grade (letter, percentage, or points)"),
    ] = None
    excused: Annotated[
        Optional[bool],
        Field(description="Whether the student has been excused from this assignment"),
    ] = None
    late: Annotated[
        Optional[bool],
        Field(description="Whether the submission was late"),
    ] = None
    missing: Annotated[
        Optional[bool],
        Field(description="Whether the submission is missing"),
    ] = None
    attempt: Annotated[
        Optional[int],
        Field(description="The submission attempt number (0 if never submitted)"),
    ] = None
    submissionType: Annotated[
        Optional[str],
        Field(description="How the submission was made", examples=["online_upload"]),
    ] = None
    submittedAt: Annotated[
        Optional[datetime],
        Field(description="When the submission was turned in"),
    ] = None
    gradedAt: Annotated[
        Optional[datetime],
        Field(description="When the submission was graded"),
    ] = None
    cachedDueDate: Annotated[
        Optional[datetime],
        Field(description="The due date that applies to this student"),
    ] = None
    user: Annotated[
        Optional[SubmissionUserRef],
        Field(description="The student the submission belongs to"),
    ] = None


class AssignmentSubmissions(BaseModel):
    """Submission status for an assignment (one entry per visible student)."""

    assignmentId: Annotated[
        str, Field(description="The numeric Canvas ID of the assignment")
    ]
    assignmentName: Annotated[
        Optional[str], Field(description="The name of the assignment")
    ] = None
    dueAt: Annotated[
        Optional[datetime], Field(description="The assignment's due date")
    ] = None
    pointsPossible: Annotated[
        Optional[float], Field(description="Maximum points possible")
    ] = None
    submissions: Annotated[
        List[SubmissionStatus],
        Field(
            description=(
                "Visible submissions. Students see only their own; "
                "teachers see all students."
            ),
        ),
    ]
