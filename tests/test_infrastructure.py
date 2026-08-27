"""Smoke tests for the Phase 0 test harness."""

from tests.fixtures.courses import ALL_COURSES_GRAPHQL
from tests.helpers.canvas_mock import make_graphql_response, make_http_response


def test_make_http_response_success() -> None:
    response = make_http_response([{"id": 1}])
    assert response.is_success
    assert response.data == [{"id": 1}]


def test_make_graphql_response_wraps_data() -> None:
    response = make_graphql_response(ALL_COURSES_GRAPHQL)
    assert response.data["data"] == ALL_COURSES_GRAPHQL


async def test_canvas_api_fixture_routes_rest(canvas_api) -> None:
    canvas_api.rest_returns("v1/ping", {"ok": True})
    response = await canvas_api.rest("v1/ping")
    assert response.data == {"ok": True}


async def test_canvas_api_fixture_routes_graphql(canvas_api) -> None:
    canvas_api.graphql_returns(ALL_COURSES_GRAPHQL)
    response = await canvas_api.graphql("query { allCourses { id } }")
    assert response.data["data"] == ALL_COURSES_GRAPHQL
