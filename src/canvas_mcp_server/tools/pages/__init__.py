"""Canvas wiki page tools."""

from typing import Final, List

from .get_course_pages import get_course_pages_tool
from .get_page import get_page_tool
from .get_page_resources import get_page_resources_tool

__all__: Final[List[str]] = [
    "get_course_pages_tool",
    "get_page_tool",
    "get_page_resources_tool",
]
