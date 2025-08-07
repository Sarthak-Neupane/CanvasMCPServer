from typing import Optional, List, Dict, Annotated
from pydantic import BaseModel, Field
from datetime import datetime

class CourseProgress(BaseModel):
    requirement_count: Annotated[
        Optional[int],
        Field(description="total number of requirements from all modules", example=10),
    ]
    requirement_completed_count: Annotated[
        Optional[int],
        Field(
            description="total number of requirements the user has completed from all modules",
            example=1,
        ),
    ]
    next_requirement_url: Annotated[
        Optional[str],
        Field(
            description="url to next module item that has an unmet requirement. null if the user has completed the course or the current module does not require sequential progress",
            example="http://localhost/courses/1/modules/items/2",
        ),
    ] = None
    completed_at: Annotated[
        Optional[datetime],
        Field(
            description="date the course was completed. null if the course has not been completed by this user",
            example="2013-06-01T00:00:00-06:00",
        ),
    ] = None

