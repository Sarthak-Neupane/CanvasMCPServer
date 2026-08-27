"""Tests for GraphQL response helpers."""

import pytest

from canvas_mcp_server.utils.canvas_api import extract_graphql_data
from canvas_mcp_server.utils.http_client import HTTPError
from tests.helpers.canvas_mock import make_graphql_response, make_http_response


def test_extract_graphql_data_success() -> None:
    response = make_graphql_response({"course": {"_id": "100001"}})

    data = extract_graphql_data(response)

    assert data == {"course": {"_id": "100001"}}


def test_extract_graphql_data_errors_array() -> None:
    response = make_http_response(
        {"errors": [{"message": "Cannot query field 'foo'"}]},
        url="https://canvas.example.edu/api/graphql",
    )

    with pytest.raises(
        HTTPError, match="Canvas GraphQL error: Cannot query field 'foo'"
    ):
        extract_graphql_data(response)


def test_extract_graphql_data_missing_data() -> None:
    response = make_http_response({"data": None})

    with pytest.raises(HTTPError, match="Canvas GraphQL response contained no data"):
        extract_graphql_data(response)


def test_extract_graphql_data_non_object_body() -> None:
    response = make_http_response("not json object")

    with pytest.raises(
        HTTPError, match="Canvas GraphQL response was not a JSON object"
    ):
        extract_graphql_data(response)
