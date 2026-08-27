"""Regression tests for submission feedback tools."""

from canvas_mcp_server.models import SubmissionFeedback
from canvas_mcp_server.tools.submissions._parse import submission_feedback_from_api
from canvas_mcp_server.tools.submissions.get_submission_feedback import (
    get_submission_feedback,
)
from tests.fixtures.grades import USERS_SELF_REST
from tests.fixtures.submissions import SUBMISSION_FEEDBACK_REST
from tests.helpers.assertions import assert_http_error
from tests.helpers.canvas_mock import CanvasAPIMock


def test_submission_feedback_from_api() -> None:
    feedback = submission_feedback_from_api(SUBMISSION_FEEDBACK_REST)
    assert feedback.assignment_id == 200001
    assert feedback.score == 9.0
    assert len(feedback.comments) == 1
    assert feedback.comments[0].author_name == "Dr. Instructor"
    assert feedback.comments[0].attachment is not None
    assert feedback.comments[0].attachment.attachment_id == 500010
    assert feedback.rubric_assessment["crit1"].points == 4.0
    assert len(feedback.attachments) == 1


async def test_get_submission_feedback_success(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns(
        "v1/courses/100001/assignments/200001/submissions/self",
        SUBMISSION_FEEDBACK_REST,
    )

    result = await get_submission_feedback("100001", "200001")

    assert isinstance(result, SubmissionFeedback)
    assert result.grade == "9"
    assert len(result.comments) == 1
    assert canvas_api.rest.await_args is not None
    includes = canvas_api.rest.await_args.kwargs["params"]["include[]"]
    assert "submission_comments" in includes
    assert "rubric_assessment" in includes


async def test_get_submission_feedback_http_error(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_error(
        "v1/courses/100001/assignments/200001/submissions/self",
        status_code=404,
        message="Not found",
    )

    result = await get_submission_feedback("100001", "200001")

    assert_http_error(result, 404)
