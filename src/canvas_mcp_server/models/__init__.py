"""Clean, modular models for Canvas courses."""
from typing import Final, List

from .courses.course_detail_model import CourseDetail
from .courses.course_calendar_model import CalendarLink
from .courses.course_progress_model import CourseProgress
from .courses.course_term_model import Term
from .courses.course_summary_model import CourseSummary

__all__: Final[List[str]] = [
    # Models for course data
    "CourseDetail"
    "CalendarLink",
    "CourseProgress",
    "Term",
    "CourseSummary",
]