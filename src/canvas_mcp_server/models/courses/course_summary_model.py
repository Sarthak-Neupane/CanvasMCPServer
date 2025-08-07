from pydantic import BaseModel
from typing import Annotated
from pydantic import Field

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
    state: Annotated[str, Field(
        default=None,
        description="The current state of the course",
        example="available"
    )]