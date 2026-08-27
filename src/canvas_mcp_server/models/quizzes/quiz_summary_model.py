"""Pydantic models for Canvas quiz summaries."""

from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field


class QuizSummary(BaseModel):
    """Summary metadata for a Canvas quiz (REST API, no questions)."""

    model_config = ConfigDict(populate_by_name=True)

    quiz_id: Annotated[
        int,
        Field(alias="id", description="The numeric Canvas ID of the quiz"),
    ]
    title: Annotated[
        Optional[str],
        Field(description="The quiz title"),
    ] = None
    html_url: Annotated[
        Optional[str],
        Field(description="Canvas web URL for the quiz"),
    ] = None
    quiz_type: Annotated[
        Optional[str],
        Field(
            description=("practice_quiz, assignment, graded_survey, or survey"),
        ),
    ] = None
    due_at: Annotated[
        Optional[datetime],
        Field(description="When the quiz is due"),
    ] = None
    unlock_at: Annotated[
        Optional[datetime],
        Field(description="When the quiz unlocks for students"),
    ] = None
    lock_at: Annotated[
        Optional[datetime],
        Field(description="When the quiz locks for students"),
    ] = None
    time_limit: Annotated[
        Optional[int],
        Field(description="Time limit in minutes, if set"),
    ] = None
    question_count: Annotated[
        Optional[int],
        Field(description="Number of questions (count only, not content)"),
    ] = None
    points_possible: Annotated[
        Optional[float],
        Field(description="Total point value"),
    ] = None
    allowed_attempts: Annotated[
        Optional[int],
        Field(description="Allowed attempts (-1 = unlimited)"),
    ] = None
    published: Annotated[
        Optional[bool],
        Field(description="Whether the quiz is published"),
    ] = None
    locked_for_user: Annotated[
        Optional[bool],
        Field(description="Whether the quiz is locked for the current user"),
    ] = None
    lock_explanation: Annotated[
        Optional[str],
        Field(description="Why the quiz is locked, when applicable"),
    ] = None
    requires_access_code: Annotated[
        Optional[bool],
        Field(description="Whether a password is required to take the quiz"),
    ] = None
    has_ip_filter: Annotated[
        Optional[bool],
        Field(description="Whether access is restricted by IP address"),
    ] = None
    shuffle_answers: Annotated[
        Optional[bool],
        Field(description="Whether answer order is shuffled"),
    ] = None
    one_question_at_a_time: Annotated[
        Optional[bool],
        Field(description="Whether the quiz shows one question at a time"),
    ] = None
