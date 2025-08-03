"""Canvas courses package with Pydantic models and comprehensive documentation."""

from typing import Final, List
from mcp.server.fastmcp.tools import Tool

from .get_courses import get_courses_tool
from .types import (
    CoursesQueryParams,
    EnrollmentType,
    EnrollmentState,
    CoursesInclude,
    CourseState,
    CourseDisplayField,
)

__all__: Final[List[str]] = [
    # Tools
    "get_courses_tool",
    
    # Pydantic Models
    "CoursesQueryParams",
    "Course", 
    "CoursesApiResponse",
    "CourseDisplayField",

    
    # Enums
    "EnrollmentType",
    "EnrollmentState", 
    "CoursesInclude",
    "CourseState",
]
