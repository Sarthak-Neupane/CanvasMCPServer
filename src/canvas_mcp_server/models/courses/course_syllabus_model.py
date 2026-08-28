from typing import Annotated, Optional

from pydantic import Field

from ..common.untrusted_content import UntrustedContentMixin
from ..files.file_model import FileDetail


class CourseSyllabus(UntrustedContentMixin):
    """Course syllabus content from the Canvas REST Courses API."""

    course_id: Annotated[
        str,
        Field(description="The numeric Canvas ID of the course", examples=["182314"]),
    ]
    course_name: Annotated[
        Optional[str],
        Field(description="The full name of the course"),
    ] = None
    source_type: Annotated[
        Optional[str],
        Field(
            default="inline_html",
            description=(
                "Syllabus origin: 'inline_html', 'canvas_file', 'external_url', or 'missing'"
            ),
        ),
    ] = "inline_html"
    text: Annotated[
        Optional[str],
        Field(
            description=(
                "Primary plain-text syllabus content (extracted from inline HTML "
                "or auto-fetched from a linked Canvas syllabus document)"
            ),
        ),
    ] = None
    syllabus_body: Annotated[
        Optional[str],
        Field(
            description=(
                "User-generated HTML for the course syllabus page "
                "(from include[]=syllabus_body)"
            ),
        ),
    ] = None
    syllabus_body_text: Annotated[
        Optional[str],
        Field(
            description="Plain text extracted from syllabus_body HTML",
        ),
    ] = None
    file: Annotated[
        Optional[FileDetail],
        Field(
            description="Metadata for the primary linked syllabus file when source_type='canvas_file'",
        ),
    ] = None
    external_url: Annotated[
        Optional[str],
        Field(
            description="Primary external syllabus URL when source_type='external_url'",
        ),
    ] = None
    extraction_status: Annotated[
        Optional[str],
        Field(
            description=(
                "Status of document text extraction: 'ok', 'empty', "
                "'text_extraction_unavailable', 'download_failed', or 'not_applicable'"
            ),
        ),
    ] = None
    syllabus_course_summary: Annotated[
        Optional[bool],
        Field(
            description=(
                "Whether the course summary (assignments and calendar events) "
                "is shown on the syllabus page, when Canvas exposes this field"
            ),
        ),
    ] = None
