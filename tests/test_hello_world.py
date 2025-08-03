"""Tests for the hello_world tool."""

import pytest
from canvas_mcp_server.tools.hello_world import hello_world, hello_world_tool


def test_hello_world_function():
    """Test the hello_world function returns the correct greeting."""
    result = hello_world()
    assert result == "Hello, World!"


def test_hello_world_tool_properties():
    """Test the hello_world_tool has correct properties."""
    assert hello_world_tool.name == "hello_world"
    assert "simple tool" in hello_world_tool.description.lower()
    assert hello_world_tool.fn == hello_world


def test_hello_world_tool_execution():
    """Test the hello_world_tool can be executed."""
    result = hello_world_tool.fn()
    assert result == "Hello, World!"
