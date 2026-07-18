from typing import Annotated, Optional

from pydantic import BaseModel, Field

from .course_term_model import Term


class CourseSummary(BaseModel):
    id: Annotated[
        str,
        Field(
            description="The unique identifier for the course",
            examples=["123456"],
        ),
    ]
    courseCode: Annotated[
        Optional[str],
        Field(
            description="The course code for the course, if defined.",
            examples=["INSTCON12"],
        ),
    ] = None
    name: Annotated[
        str,
        Field(
            description="The full name of the course",
            examples=["InstructureCon 2012"],
        ),
    ]
    term: Annotated[
        Optional[Term],
        Field(description="The term associated with the course, if any."),
    ] = None
