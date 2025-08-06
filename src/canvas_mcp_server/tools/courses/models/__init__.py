"""Clean, modular models for Canvas courses."""
from typing import Final, List

from .course_model import Course
from .course_calendar_model import CalendarLink
from .course_progress_model import CourseProgress
from .course_query_model import (
    CoursesQueryParams, 
    PerCourseQueryParams,
)
from .course_term_model import Term

__all__: Final[List[str]] = [
    # Models for course data
    "Course"
    "CalendarLink",
    "CourseProgress",
    "Term",
    "CoursesQueryParams",
    "PerCourseQueryParams",
]