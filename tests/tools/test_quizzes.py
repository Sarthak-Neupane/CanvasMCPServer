"""Regression tests for quiz MCP tools."""

from canvas_mcp_server.models import QuizDetail, QuizSummary
from canvas_mcp_server.tools.quizzes._parse import sanitize_quiz_api_payload
from canvas_mcp_server.tools.quizzes.get_course_quizzes import get_course_quizzes
from canvas_mcp_server.tools.quizzes.get_quiz import get_quiz
from tests.fixtures.quizzes import QUIZZES_LIST_REST, QUIZ_DETAIL_REST
from tests.helpers.assertions import assert_http_error, assert_list_result
from tests.helpers.canvas_mock import CanvasAPIMock


def test_sanitize_quiz_api_payload_strips_secrets() -> None:
    sanitized = sanitize_quiz_api_payload(
        {"id": 1, "access_code": "abc", "ip_filter": "1.2.3.4"}
    )
    assert "access_code" not in sanitized
    assert "ip_filter" not in sanitized
    assert sanitized["requires_access_code"] is True
    assert sanitized["has_ip_filter"] is True


async def test_get_course_quizzes_success(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns("v1/courses/100001/quizzes", QUIZZES_LIST_REST)

    result = await get_course_quizzes("100001")

    assert result.result_count == 2
    assert all(isinstance(quiz, QuizSummary) for quiz in result.results)
    assert result.results[0].quiz_id == 500001
    assert result.results[0].requires_access_code is True
    assert result.results[0].has_ip_filter is False
    assert result.results[1].locked_for_user is True
    assert result.results[1].has_ip_filter is True


async def test_get_course_quizzes_search_term(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns("v1/courses/100001/quizzes", QUIZZES_LIST_REST)

    await get_course_quizzes("100001", search_term="Quiz 1")

    assert canvas_api.get_rest_paginated_mock.await_args is not None
    assert (
        canvas_api.get_rest_paginated_mock.await_args.kwargs["params"]["search_term"]
        == "Quiz 1"
    )


async def test_get_quiz_success(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns(
        "v1/courses/100001/quizzes/500001",
        QUIZ_DETAIL_REST,
    )

    result = await get_quiz("100001", "500001")

    assert isinstance(result, QuizDetail)
    assert result.title == "Quiz 1"
    assert result.description_text == "Cover chapters 1-3."
    assert result.requires_access_code is True
    assert result.question_types == ["multiple_choice", "essay"]
    assert result.scoring_policy == "keep_highest"


async def test_get_quiz_http_error(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_error(
        "v1/courses/100001/quizzes/500001",
        status_code=404,
        message="Not found",
    )

    result = await get_quiz("100001", "500001")

    assert_http_error(result, 404)
