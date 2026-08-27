"""Canvas quiz tools."""

from typing import Final, List

from .get_course_quizzes import get_course_quizzes_tool
from .get_quiz import get_quiz_tool

__all__: Final[List[str]] = [
    "get_course_quizzes_tool",
    "get_quiz_tool",
]
