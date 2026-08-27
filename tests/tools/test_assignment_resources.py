"""Regression tests for get_assignment_resources."""

from canvas_mcp_server.models import AssignmentResourceType, AssignmentResources
from canvas_mcp_server.tools.assignments._resources import (
    parse_assignment_resources_from_html,
)
from canvas_mcp_server.tools.assignments.get_assignment_resources import (
    get_assignment_resources,
)
from tests.fixtures.assignments import ASSIGNMENT_REST_WITH_EMBEDS
from tests.fixtures.html_snippets import ASSIGNMENT_DESCRIPTION_HTML
from tests.helpers.assertions import assert_http_error
from tests.helpers.canvas_mock import CanvasAPIMock


def test_parse_assignment_resources_dedupes_file_embeds() -> None:
    resources = parse_assignment_resources_from_html(
        ASSIGNMENT_DESCRIPTION_HTML,
        default_course_id="100001",
    )

    types = [resource.type for resource in resources]
    assert types.count(AssignmentResourceType.FILE) == 1
    assert AssignmentResourceType.PAGE in types
    assert AssignmentResourceType.EXTERNAL_URL in types


async def test_get_assignment_resources_success(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_returns(
        "v1/courses/100001/assignments/200001",
        ASSIGNMENT_REST_WITH_EMBEDS,
    )

    result = await get_assignment_resources("100001", "200001")

    assert isinstance(result, AssignmentResources)
    assert result.assignment_id == "200001"
    assert result.assignment_name == "Homework 1"
    assert len(result.resources) == 3

    file_resource = next(
        r for r in result.resources if r.type == AssignmentResourceType.FILE
    )
    assert file_resource.id == "500001"
    assert file_resource.course_id == "100001"
    assert file_resource.label == "worksheet.pdf"

    page_resource = next(
        r for r in result.resources if r.type == AssignmentResourceType.PAGE
    )
    assert page_resource.id == "week-1"


async def test_get_assignment_resources_empty_description(
    canvas_api: CanvasAPIMock,
) -> None:
    canvas_api.rest_returns(
        "v1/courses/100001/assignments/200001",
        {"id": 200001, "name": "No links", "description": "<p>Nothing here</p>"},
    )

    result = await get_assignment_resources("100001", "200001")

    assert isinstance(result, AssignmentResources)
    assert result.resources == []


async def test_get_assignment_resources_not_found(canvas_api: CanvasAPIMock) -> None:
    canvas_api.rest_error(
        "v1/courses/100001/assignments/999999",
        status_code=404,
        message="Not found",
    )

    result = await get_assignment_resources("100001", "999999")

    assert_http_error(result, 404)
