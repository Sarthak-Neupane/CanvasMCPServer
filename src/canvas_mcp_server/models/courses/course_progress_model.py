from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field


class CourseProgress(BaseModel):
    requirement_count: Annotated[
        Optional[int],
        Field(
            description="total number of requirements from all modules",
            examples=[10],
        ),
    ] = None
    requirement_completed_count: Annotated[
        Optional[int],
        Field(
            description="total number of requirements the user has completed from all modules",
            examples=[1],
        ),
    ] = None
    next_requirement_url: Annotated[
        Optional[str],
        Field(
            description=(
                "url to next module item that has an unmet requirement. null if "
                "the user has completed the course or the current module does "
                "not require sequential progress"
            ),
            examples=["http://localhost/courses/1/modules/items/2"],
        ),
    ] = None
    completed_at: Annotated[
        Optional[datetime],
        Field(
            description=(
                "date the course was completed. null if the course has not "
                "been completed by this user"
            ),
            examples=["2013-06-01T00:00:00-06:00"],
        ),
    ] = None
