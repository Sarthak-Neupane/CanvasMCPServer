from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field


class AssignmentSummary(BaseModel):
    id: Annotated[
        str,
        Field(
            alias="_id",
            description="The numeric Canvas ID of the assignment",
            examples=["987654"],
        ),
    ]
    name: Annotated[
        str,
        Field(description="The name of the assignment", examples=["Essay 1"]),
    ]
    dueAt: Annotated[
        Optional[datetime],
        Field(description="When the assignment is due, if a due date is set"),
    ] = None
    pointsPossible: Annotated[
        Optional[float],
        Field(description="The maximum points possible", examples=[100.0]),
    ] = None
    state: Annotated[
        Optional[str],
        Field(
            description="The workflow state of the assignment",
            examples=["published"],
        ),
    ] = None
    htmlUrl: Annotated[
        Optional[str],
        Field(description="Link to the assignment in the Canvas web UI"),
    ] = None
