"""Canvas courses query parameters - focused and clean."""

from typing import Optional, List, Annotated, Union
from pydantic import BaseModel, Field, ConfigDict

from ..constants.course_query_includes import CoursesInclude, PerCourseInclude
from ..constants.course_enrollment_constants import (
    EnrollmentType,
    EnrollmentState
)
from ..constants.course_workflow_state import WorkflowState

class CoursesQueryParams(BaseModel):
    """
    Parameters for Canvas courses API query.
    
    Clean, focused parameter model without excessive documentation.
    """
    
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    # Enrollment filtering
    enrollment_type: Optional[EnrollmentType] = Field(
        default=EnrollmentType.STUDENT,
        description="Filter by user's enrollment type (teacher, student, etc.)"
    )
    
    enrollment_state: Optional[EnrollmentState] = Field(
        default=EnrollmentState.ACTIVE,
        description="Filter by enrollment state (active, completed, etc.)"
    )
    
    exclude_blueprint_courses: Optional[bool] = Field(
        default=False,
        description="Exclude blueprint courses from results"
    )
    
    # Include additional data
    include: Optional[List[CoursesInclude]] = Field(
        default_factory=list,
        description="Additional information to include with each course"
    )
    
    # Course state filtering  
    state: Optional[WorkflowState] = Field(
        default=WorkflowState.AVAILABLE,
        description="Filter by course publication state (unpublished, available, etc.)"
    )

class PerCourseQueryParams(BaseModel):
    """
    Parameters for per-course API query.
    
    Focused on per-course data retrieval.
    """
    
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    course_id: Annotated[
        int, Field(description="Course ID to retrieve", example=370663)
    ]
    
    include: Optional[List[Union[CoursesInclude, PerCourseInclude]]] = Field(
        default=None,
        description="Additional information to include (sections, teachers, total_students, etc.)"
    )

    def to_dict(self) -> dict:
        """Convert to dictionary for API requests."""
        return self.model_dump(exclude_none=True)