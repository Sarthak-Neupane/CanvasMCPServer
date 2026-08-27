"""Regression tests for rubric MCP tools."""

from canvas_mcp_server.models import Rubric
from canvas_mcp_server.tools.rubrics._parse import rubric_from_assignment
from canvas_mcp_server.tools.rubrics.get_assignment_rubric import (
    get_assignment_rubric,
)
from tests.fixtures.rubrics import (
    ASSIGNMENT_WITHOUT_RUBRIC_REST,
    ASSIGNMENT_WITH_RUBRIC_REST,
)
from tests.helpers.assertions import assert_http_error
from tests.helpers.canvas_mock import CanvasAPIMock


def test_rubric_from_assignment() -> None:
    rubric = rubric_from_assignment(ASSIGNMENT_WITH_RUBRIC_REST)
    assert rubric is not None
    assert rubric.assignment_id == 200001
    assert rubric.points_possible == 12.0
    assert rubric.use_rubric_for_grading is True
    assert len(rubric.criteria) == 2
    assert rubric.criteria[0].criterion_id == "crit1"
    assert len(rubric.criteria[0].ratings) == 2
    assert rubric.criteria[0].ratings[0].rating_id == "rat1"


async def test_get_assignment_rubric_success(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns(
        "v1/courses/100001/assignments/200001",
        ASSIGNMENT_WITH_RUBRIC_REST,
    )

    result = await get_assignment_rubric("100001", "200001")

    assert isinstance(result, Rubric)
    assert result.assignment_id == 200001
    assert len(result.criteria) == 2
    assert canvas_api.rest.await_args is not None
    assert canvas_api.rest.await_args.kwargs["params"]["include[]"] == "rubric"


async def test_get_assignment_rubric_not_found(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns(
        "v1/courses/100001/assignments/200002",
        ASSIGNMENT_WITHOUT_RUBRIC_REST,
    )

    result = await get_assignment_rubric("100001", "200002")

    assert isinstance(result, dict)
    assert result["error"] == "Not Found"
    assert "no rubric" in result["message"].lower()


async def test_get_assignment_rubric_http_error(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_error(
        "v1/courses/100001/assignments/200001",
        status_code=404,
        message="Not found",
    )

    result = await get_assignment_rubric("100001", "200001")

    assert_http_error(result, 404)
