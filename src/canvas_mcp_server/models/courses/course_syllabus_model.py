from typing import Annotated, Optional

from pydantic import BaseModel, Field

from ..common.untrusted_content import UntrustedContentMixin


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
    syllabus_body: Annotated[
        Optional[str],
        Field(
            description=(
                "User-generated HTML for the course syllabus page "
                "(from include[]=syllabus_body)"
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
