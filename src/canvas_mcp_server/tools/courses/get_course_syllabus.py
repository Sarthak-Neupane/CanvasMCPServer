"""Tool for fetching a Canvas course syllabus via the REST API.

Uses GET /api/v1/courses/:course_id with include[]=syllabus_body.
Auto-follows primary Canvas syllabus file references to extract plain text
so agents do not have to chain multiple file tools.
"""

from typing import Annotated, Any, Dict, Final, Optional, TypeAlias, Union

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...errors import as_tool_error
from ...models import CourseSyllabus, FileDetail
from ...utils import canvas_api_client
from ...utils.content_metadata import attach_content_metadata
from ...utils.document_text import extract_text_from_bytes
from ...utils.html import extract_canvas_resource_references, html_to_text

CourseSyllabusResponse: TypeAlias = Union[CourseSyllabus, Dict[str, Any]]


async def get_course_syllabus(
    course_id: Annotated[
        str,
        Field(
            description=("The course ID (numeric Canvas ID, e.g. '182314')."),
        ),
    ],
) -> CourseSyllabusResponse:
    """
    Get the syllabus for a Canvas course.

    Returns course id, name, source_type ('inline_html', 'canvas_file', 'external_url',
    or 'missing'), primary readable text, syllabus_body (HTML), and linked file details.
    When the syllabus is an uploaded document (e.g. PDF, DOCX, TXT), automatically fetches
    the file and extracts readable text.

    Returns an error object with "error", "message", and optionally
    "status_code" keys on failure.
    """
    try:
        response = await canvas_api_client.get_rest(
            endpoint=f"v1/courses/{course_id}",
            params={"include[]": "syllabus_body"},
        )
        data = response.data
        if not isinstance(data, dict):
            raise Exception("Canvas course response was not an object")

        syllabus_body = data.get("syllabus_body")
        body_text = html_to_text(syllabus_body) if syllabus_body else ""

        source_type = "missing"
        text: Optional[str] = None
        file_detail: Optional[FileDetail] = None
        external_url: Optional[str] = None
        extraction_status: Optional[str] = None

        if not syllabus_body or not syllabus_body.strip():
            source_type = "missing"
            extraction_status = "empty"
        else:
            resource_refs = extract_canvas_resource_references(syllabus_body)
            file_ref = next(
                (r for r in resource_refs if r.get("type") == "file" and r.get("id")),
                None,
            )
            ext_ref = next(
                (
                    r
                    for r in resource_refs
                    if r.get("type") == "external_url" and r.get("url")
                ),
                None,
            )

            # If body has minimal inline text and points to a Canvas file, auto-follow file
            if file_ref and (len(body_text) < 150 or not body_text):
                source_type = "canvas_file"
                file_id = file_ref["id"]
                try:
                    file_resp = await canvas_api_client.get_rest(f"v1/files/{file_id}")
                    if isinstance(file_resp.data, dict):
                        file_detail = FileDetail.model_validate(file_resp.data)
                        if file_detail.url:
                            try:
                                content_bytes = (
                                    await canvas_api_client.download_file_bytes(
                                        file_detail.url
                                    )
                                )
                                doc_text, status = extract_text_from_bytes(
                                    content_bytes,
                                    filename=(
                                        file_detail.display_name or file_detail.filename
                                    ),
                                    content_type=file_detail.content_type,
                                )
                                text = doc_text
                                extraction_status = status
                            except Exception:
                                extraction_status = "download_failed"
                except Exception:
                    extraction_status = "download_failed"
            elif ext_ref and (len(body_text) < 150 or not body_text):
                source_type = "external_url"
                external_url = ext_ref.get("url")
                text = body_text if body_text else None
                extraction_status = "not_applicable"
            else:
                source_type = "inline_html"
                text = body_text
                extraction_status = "ok"

        syllabus = CourseSyllabus(
            course_id=str(data.get("id", course_id)),
            course_name=data.get("name"),
            source_type=source_type,
            text=text,
            syllabus_body=syllabus_body,
            syllabus_body_text=body_text if body_text else None,
            file=file_detail,
            external_url=external_url,
            extraction_status=extraction_status,
            syllabus_course_summary=data.get("syllabus_course_summary"),
        )
        return attach_content_metadata(
            syllabus,
            source_type=source_type,
            course_id=syllabus.course_id,
            resource_id=syllabus.course_id,
        )

    except Exception as e:
        return as_tool_error(e, source="canvas_rest")


get_course_syllabus_tool: Final[Tool] = Tool.from_function(
    name="get_course_syllabus",
    description=(
        "Get a Canvas course syllabus: source_type ('inline_html', 'canvas_file', "
        "'external_url', 'missing'), primary readable text, HTML body, and auto-extracted "
        "file content when the syllabus is an uploaded document (PDF, DOCX, TXT). "
        "Use for attendance policy, grading weights, exam rules, and course policies."
    ),
    fn=get_course_syllabus,
)
