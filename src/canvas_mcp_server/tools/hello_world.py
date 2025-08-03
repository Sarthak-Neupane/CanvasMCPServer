"""Hello World tool for Canvas MCP Server."""

from mcp.server.fastmcp.tools import Tool


def hello_world() -> str:
    """
    A simple greeting tool that returns 'Hello, World!'.
    
    Returns:
        str: A greeting message
    """
    return "Hello, World!"


# Export the tool
hello_world_tool = Tool.from_function(
    name="hello_world",
    description="A simple tool that returns 'Hello, World!' - useful for testing the server",
    fn=hello_world,
)
