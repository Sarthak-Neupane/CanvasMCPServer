"""Canvas MCP Server tools package."""

from typing import Final, List
from mcp.server.fastmcp.tools import Tool

from .announcements import get_announcements_tool
from .assignments import (
    get_assignment_details_tool,
    get_assignment_resources_tool,
    get_assignments_for_course_tool,
    get_upcoming_assignments_tool,
)
from .courses import (
    get_all_courses_tool,
    get_course_by_id_tool,
    get_course_syllabus_tool,
)
from .downloads import (
    download_assignment_files_tool,
    download_course_files_tool,
    download_file_tool,
    download_module_files_tool,
)
from .files import (
    get_course_files_tool,
    get_course_folders_tool,
    get_file_details_tool,
    get_folder_files_tool,
)
from .grades import get_course_grades_tool
from .modules import (
    get_course_modules_tool,
    get_module_item_details_tool,
    get_module_items_tool,
)
from .pages import get_course_pages_tool, get_page_tool
from .planner import get_planner_items_tool
from .submissions import get_submission_status_tool
from .todos import get_todo_items_tool

ALL_TOOLS: Final[List[Tool]] = [
    get_all_courses_tool,
    get_course_by_id_tool,
    get_course_syllabus_tool,
    get_course_pages_tool,
    get_page_tool,
    get_planner_items_tool,
    get_course_files_tool,
    get_course_folders_tool,
    get_folder_files_tool,
    get_file_details_tool,
    download_file_tool,
    download_course_files_tool,
    download_module_files_tool,
    download_assignment_files_tool,
    get_upcoming_assignments_tool,
    get_assignments_for_course_tool,
    get_assignment_details_tool,
    get_assignment_resources_tool,
    get_todo_items_tool,
    get_submission_status_tool,
    get_course_grades_tool,
    get_announcements_tool,
    get_course_modules_tool,
    get_module_items_tool,
    get_module_item_details_tool,
]

__all__: Final[List[str]] = [
    "ALL_TOOLS",
    "get_all_courses_tool",
    "get_course_by_id_tool",
    "get_course_syllabus_tool",
    "get_course_pages_tool",
    "get_page_tool",
    "get_planner_items_tool",
    "get_course_files_tool",
    "get_course_folders_tool",
    "get_folder_files_tool",
    "get_file_details_tool",
    "download_file_tool",
    "download_course_files_tool",
    "download_module_files_tool",
    "download_assignment_files_tool",
    "get_upcoming_assignments_tool",
    "get_assignments_for_course_tool",
    "get_assignment_details_tool",
    "get_assignment_resources_tool",
    "get_todo_items_tool",
    "get_submission_status_tool",
    "get_course_grades_tool",
    "get_announcements_tool",
    "get_course_modules_tool",
    "get_module_items_tool",
    "get_module_item_details_tool",
]
