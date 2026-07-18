from typing import Annotated

from pydantic import BaseModel, Field

from ...constants import WorkflowState


class CourseDetail(BaseModel):
    id: Annotated[
        str,
        Field(
            description="the unique identifier for the course",
            examples=["370663"],
        ),
    ]
    name: Annotated[
        str,
        Field(
            description="the full name of the course",
            examples=["InstructureCon 2012"],
        ),
    ]
    courseCode: Annotated[
        str,
        Field(description="the course code", examples=["INSTCON12"]),
    ]
    state: Annotated[
        WorkflowState,
        Field(
            description="the current state of the course",
            examples=["available"],
        ),
    ]
