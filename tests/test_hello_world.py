"""Tests for the hello_world tool."""

import pytest
from typing import Final
from canvas_mcp_server.tools.hello_world import hello_world, hello_world_tool


def test_hello_world_function() -> None:
    """Test the hello_world function returns the correct greeting."""
    result: str = hello_world()
    expected: Final[str] = "Hello, World!"
    assert result == expected


def test_hello_world_tool_properties() -> None:
    """Test the hello_world_tool has correct properties."""
    expected_name: Final[str] = "hello_world"
    assert hello_world_tool.name == expected_name
    assert "simple tool" in hello_world_tool.description.lower()
    assert hello_world_tool.fn == hello_world


def test_hello_world_tool_execution() -> None:
    """Test the hello_world_tool can be executed."""
    result: str = hello_world_tool.fn()
    expected: Final[str] = "Hello, World!"
    assert result == expected
