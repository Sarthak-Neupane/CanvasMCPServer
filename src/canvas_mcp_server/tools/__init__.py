"""Canvas MCP Server tools package with Pydantic models."""

from typing import Final, List
from mcp.server.fastmcp.tools import Tool

from .courses import get_all_courses_tool, get_course_by_id_tool

__all__: Final[List[str]] = [
    "get_all_courses_tool",
    "get_course_by_id_tool"
]
