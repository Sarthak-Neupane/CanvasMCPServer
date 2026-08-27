"""Pydantic models for full Canvas quiz metadata."""

from typing import Annotated, List, Optional

from pydantic import Field

from .quiz_summary_model import QuizSummary


class QuizDetail(QuizSummary):
    """Full quiz metadata including description (no question content)."""

    description: Annotated[
        Optional[str],
        Field(description="Quiz instructions as HTML"),
    ] = None
    description_text: Annotated[
        Optional[str],
        Field(
            description=(
                "Plain-text instructions (populated by get_quiz when HTML "
                "is present)"
            ),
        ),
    ] = None
    scoring_policy: Annotated[
        Optional[str],
        Field(description="keep_highest or keep_latest when retries allowed"),
    ] = None
    hide_results: Annotated[
        Optional[str],
        Field(
            description=(
                "When students can see results: null, always, or "
                "until_after_last_attempt"
            ),
        ),
    ] = None
    show_correct_answers: Annotated[
        Optional[bool],
        Field(description="Whether correct answers may be shown"),
    ] = None
    cant_go_back: Annotated[
        Optional[bool],
        Field(
            description=(
                "Whether questions lock after answering (one-at-a-time mode)"
            ),
        ),
    ] = None
    question_types: Annotated[
        Optional[List[str]],
        Field(
            description=(
                "Question type labels present in the quiz (metadata only)"
            ),
        ),
    ] = None
    assignment_group_id: Annotated[
        Optional[int],
        Field(description="Assignment group id for graded quizzes"),
    ] = None
