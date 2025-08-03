"""Clean, modular types package for Canvas courses."""

from typing import Final, List

# Import all the components from their focused modules
from .enums import (
    EnrollmentType,
    EnrollmentState,
    CourseState,
    CoursesInclude
)

from .course_fields import (
    CourseDisplayField,
    DETAILED_FIELDS
)

from .query_params import CoursesQueryParams

# Clean exports - everything you need for Canvas courses
__all__: Final[List[str]] = [
    # Enums for filtering and configuration
    "EnrollmentType",
    "EnrollmentState", 
    "CourseState",
    "CoursesInclude",
    
    # Field selection and display
    "CourseDisplayField",
    "ESSENTIAL_FIELDS",
    "DETAILED_FIELDS",
    
    # Models for requests and responses
    "CoursesQueryParams",
]