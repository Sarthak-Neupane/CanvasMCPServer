"""Canvas MCP Server - A Model Context Protocol server for Canvas tools."""

from typing import Final, List, Callable
from .server import main

__version__: Final[str] = "0.1.0"
__author__: Final[str] = "Sarthak Neupane"
__description__: Final[str] = "A Model Context Protocol server for Canvas tools"

__all__: Final[List[str]] = ["main"]
