"""Canvas assignment tools."""

from typing import Final, List

from .get_assignment_details import get_assignment_details_tool
from .get_assignments_for_course import get_assignments_for_course_tool
from .get_upcoming_assignments import get_upcoming_assignments_tool

__all__: Final[List[str]] = [
    "get_assignments_for_course_tool",
    "get_assignment_details_tool",
    "get_upcoming_assignments_tool",
]
