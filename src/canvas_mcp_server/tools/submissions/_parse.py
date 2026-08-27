"""Helpers for Canvas submission feedback REST responses."""

from __future__ import annotations

from typing import Any, Dict, List

from ...models import (
    RubricAssessmentEntry,
    SubmissionFeedback,
    SubmissionFeedbackAttachment,
    SubmissionFeedbackComment,
)


def _attachments_from_submission(
    raw: Dict[str, Any],
) -> List[SubmissionFeedbackAttachment]:
    attachments_raw = raw.get("attachments")
    if not isinstance(attachments_raw, list):
        return []
    attachments: List[SubmissionFeedbackAttachment] = []
    for item in attachments_raw:
        if isinstance(item, dict):
            attachments.append(SubmissionFeedbackAttachment.model_validate(item))
    return attachments


def _comments_from_submission(raw: Dict[str, Any]) -> List[SubmissionFeedbackComment]:
    comments_raw = raw.get("submission_comments")
    if not isinstance(comments_raw, list):
        return []
    return [
        SubmissionFeedbackComment.model_validate(comment)
        for comment in comments_raw
        if isinstance(comment, dict)
    ]


def _rubric_assessment_from_submission(
    raw: Dict[str, Any],
) -> Dict[str, RubricAssessmentEntry]:
    assessment_raw = raw.get("rubric_assessment")
    if not isinstance(assessment_raw, dict):
        return {}
    assessment: Dict[str, RubricAssessmentEntry] = {}
    for criterion_id, entry in assessment_raw.items():
        if isinstance(entry, dict):
            assessment[str(criterion_id)] = RubricAssessmentEntry.model_validate(entry)
    return assessment


def submission_feedback_from_api(raw: Dict[str, Any]) -> SubmissionFeedback:
    """Convert a Canvas submission JSON object to SubmissionFeedback."""
    return SubmissionFeedback(
        assignment_id=raw.get("assignment_id"),
        user_id=raw.get("user_id"),
        grade=raw.get("grade"),
        score=raw.get("score"),
        workflow_state=raw.get("workflow_state"),
        submitted_at=raw.get("submitted_at"),
        graded_at=raw.get("graded_at"),
        comments=_comments_from_submission(raw),
        rubric_assessment=_rubric_assessment_from_submission(raw),
        attachments=_attachments_from_submission(raw),
    )
