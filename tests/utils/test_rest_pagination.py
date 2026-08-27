"""Tests for Canvas REST Link header pagination helpers."""

from canvas_mcp_server.utils.rest_pagination import parse_link_header


def test_parse_link_header_extracts_rel_urls() -> None:
    header = (
        "<https://canvas.example.edu/api/v1/courses/1/files?page=1&per_page=100>; "
        'rel="current", '
        "<https://canvas.example.edu/api/v1/courses/1/files?page=2&per_page=100>; "
        'rel="next", '
        "<https://canvas.example.edu/api/v1/courses/1/files?page=1&per_page=100>; "
        'rel="first"'
    )

    links = parse_link_header(header)

    assert links["current"].endswith("page=1&per_page=100")
    assert links["next"].endswith("page=2&per_page=100")
    assert links["first"].endswith("page=1&per_page=100")


def test_parse_link_header_empty_input() -> None:
    assert parse_link_header("") == {}
