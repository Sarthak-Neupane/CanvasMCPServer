"""Canvas courses query parameters - focused and clean."""

from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from .enums import EnrollmentType, EnrollmentState, CourseState, CoursesInclude


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
        default=None,
        description="Exclude blueprint courses from results"
    )
    
    # Include additional data
    include: Optional[List[CoursesInclude]] = Field(
        default=None,
        description="Additional information to include with each course"
    )
    
    # Course state filtering  
    state: Optional[List[CourseState]] = Field(
        default=None,
        description="Filter by course workflow state"
    )