from pydantic import BaseModel
from typing import Annotated
from pydantic import Field
from .course_term_model import Term

class CourseSummary(BaseModel):
    id: Annotated[str, Field(
        default=None,
        description="The unique identifier for the course",
        example="123456"
    )]
    courseCode: Annotated[str, Field(
        default=None,
        description="The course code for the course, if defined.",
        example="INSTCON12"
    )]
    name: Annotated[str, Field(
        default=None,
        description="The full name of the course",
        example="InstructureCon 2012"
    )]
    term: Annotated[Term | None, Field(
        default=None,
        description="The term associated with the course, if any."
    )] = None