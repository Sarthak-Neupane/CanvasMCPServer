"""Pydantic models for Canvas submission feedback."""

from datetime import datetime
from typing import Annotated, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class SubmissionFeedbackAttachment(BaseModel):
    """File attached to a submission or comment."""

    model_config = ConfigDict(populate_by_name=True)

    attachment_id: Annotated[
        Optional[int],
        Field(alias="id", description="Canvas file id"),
    ] = None
    filename: Annotated[
        Optional[str],
        Field(description="Stored filename"),
    ] = None
    display_name: Annotated[
        Optional[str],
        Field(description="Display name for the file"),
    ] = None
    content_type: Annotated[
        Optional[str],
        Field(alias="content-type", description="MIME type"),
    ] = None
    url: Annotated[
        Optional[str],
        Field(description="Authenticated download URL"),
    ] = None


class SubmissionFeedbackComment(BaseModel):
    """Instructor or grader comment on a submission."""

    model_config = ConfigDict(populate_by_name=True)

    comment_id: Annotated[
        int,
        Field(alias="id", description="Canvas comment id"),
    ]
    author_id: Annotated[
        Optional[int],
        Field(description="Canvas user id of the comment author"),
    ] = None
    author_name: Annotated[
        Optional[str],
        Field(description="Display name of the comment author"),
    ] = None
    comment: Annotated[
        Optional[str],
        Field(description="Comment text"),
    ] = None
    created_at: Annotated[
        Optional[datetime],
        Field(description="When the comment was created"),
    ] = None
    edited_at: Annotated[
        Optional[datetime],
        Field(description="When the comment was last edited"),
    ] = None
    attachment: Annotated[
        Optional[SubmissionFeedbackAttachment],
        Field(description="Optional file attached to the comment"),
    ] = None


class RubricAssessmentEntry(BaseModel):
    """Grader's rubric score for one criterion on a submission."""

    points: Annotated[
        Optional[float],
        Field(description="Points awarded for the criterion"),
    ] = None
    rating_id: Annotated[
        Optional[str],
        Field(description="Selected rubric rating id"),
    ] = None
    comments: Annotated[
        Optional[str],
        Field(description="Grader comments for this criterion"),
    ] = None


class SubmissionFeedback(BaseModel):
    """Feedback on the current user's submission for an assignment."""

    assignment_id: Annotated[
        Optional[int],
        Field(description="Canvas assignment id"),
    ] = None
    user_id: Annotated[
        Optional[int],
        Field(description="Canvas user id of the submitter"),
    ] = None
    grade: Annotated[
        Optional[str],
        Field(description="Posted grade in the assignment grading scheme"),
    ] = None
    score: Annotated[
        Optional[float],
        Field(description="Raw score when visible"),
    ] = None
    workflow_state: Annotated[
        Optional[str],
        Field(description="Submission workflow state"),
    ] = None
    submitted_at: Annotated[
        Optional[datetime],
        Field(description="When the submission was turned in"),
    ] = None
    graded_at: Annotated[
        Optional[datetime],
        Field(description="When the submission was graded"),
    ] = None
    comments: Annotated[
        List[SubmissionFeedbackComment],
        Field(
            default_factory=list,
            description="Submission comments from graders",
        ),
    ]
    rubric_assessment: Annotated[
        Dict[str, RubricAssessmentEntry],
        Field(
            default_factory=dict,
            description=(
                "Rubric scores keyed by criterion id (only when graded with "
                "a rubric)"
            ),
        ),
    ]
    attachments: Annotated[
        List[SubmissionFeedbackAttachment],
        Field(
            default_factory=list,
            description="Files attached to the submission",
        ),
    ]
