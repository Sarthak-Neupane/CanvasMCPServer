from typing import Annotated, Optional

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
        Optional[str],
        Field(
            description="the full name of the course",
            examples=["InstructureCon 2012"],
        ),
    ] = None
    courseCode: Annotated[
        Optional[str],
        Field(description="the course code", examples=["INSTCON12"]),
    ] = None
    state: Annotated[
        WorkflowState,
        Field(
            description="the current state of the course",
            examples=["available"],
        ),
    ]
