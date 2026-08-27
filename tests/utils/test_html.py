"""Tests for Canvas HTML utility helpers."""

from canvas_mcp_server.utils.file_download import extract_file_ids_from_html
from canvas_mcp_server.utils.html import (
    extract_canvas_links,
    extract_canvas_resource_references,
    html_to_text,
)
from tests.fixtures.html_snippets import ASSIGNMENT_DESCRIPTION_HTML, SYLLABUS_HTML


def test_html_to_text_strips_script_and_style() -> None:
    text = html_to_text(ASSIGNMENT_DESCRIPTION_HTML)

    assert "ignore me" not in text
    assert "Week 1 page" in text
    assert "worksheet.pdf" in text
    assert "external resource" in text


def test_extract_canvas_links() -> None:
    links = extract_canvas_links(ASSIGNMENT_DESCRIPTION_HTML)

    hrefs = [link["href"] for link in links]
    assert "/courses/100001/pages/week-1" in hrefs
    assert "/courses/100001/files/500001/download?wrap=1" in hrefs
    assert "https://example.edu/resource" in hrefs


def test_extract_canvas_resource_references() -> None:
    references = extract_canvas_resource_references(ASSIGNMENT_DESCRIPTION_HTML)

    by_type = {ref["type"]: ref for ref in references}
    assert by_type["page"]["id"] == "week-1"
    assert by_type["page"]["course_id"] == "100001"
    assert by_type["file"]["id"] == "500001"
    assert by_type["external_url"]["url"] == "https://example.edu/resource"


def test_extract_canvas_resource_references_dedupes_links_and_api_endpoints() -> None:
    references = extract_canvas_resource_references(ASSIGNMENT_DESCRIPTION_HTML)

    file_refs = [ref for ref in references if ref["type"] == "file"]
    assert len(file_refs) == 1


def test_extract_canvas_resource_references_assignment_link() -> None:
    references = extract_canvas_resource_references(SYLLABUS_HTML)

    assert references[0]["type"] == "assignment"
    assert references[0]["id"] == "200001"
    assert references[0]["course_id"] == "100001"


def test_extract_file_ids_from_html_delegates_to_html_utils() -> None:
    assert extract_file_ids_from_html(ASSIGNMENT_DESCRIPTION_HTML) == ["500001"]
    assert extract_file_ids_from_html(None) == []
