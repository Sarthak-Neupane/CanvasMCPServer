"""Main Canvas MCP Server implementation."""

import os
import signal
import sys
from typing import List
from asyncio import CancelledError

from anyio import create_task_group, open_signal_receiver, run
from anyio.abc import CancelScope
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.tools import Tool
from mcp.server.fastmcp.prompts import Prompt

from .tools import get_courses_tool


async def signal_handler(scope: CancelScope) -> None:
    """
    Handle SIGINT and SIGTERM signals asynchronously.

    The anyio.open_signal_receiver returns an async generator that yields signal numbers
    whenever a specified signal is received. The async for loop waits for signals and processes
    them as they arrive.
    
    Args:
        scope: The cancel scope to use for graceful shutdown.
    """
    with open_signal_receiver(signal.SIGINT, signal.SIGTERM) as signals:
        async for sig_num in signals:  # shutting down regardless of the signal type
            print(f"Received signal {sig_num}, shutting down gracefully...", file=sys.stderr)
            scope.cancel()
            return


async def run_server() -> None:
    """
    Run the MCP server with signal handling.
    
    Raises:
        Exception: If server startup or operation fails.
    """
    mcp: FastMCP = FastMCP(
        name="CanvasMCPServer",
        instructions="Canvas MCP Server - A Model Context Protocol server for Canvas tools",
    )

    tools: List[Tool] = [get_courses_tool]
    for tool in tools:
        mcp.add_tool(tool.fn, tool.name, tool.description)

    # Register prompts (empty for now)
    prompts: List[Prompt] = []  # Type will be more specific when prompts are added
    for prompt in prompts:
        mcp.add_prompt(prompt)

    try:
        async with create_task_group() as tg:
            tg.start_soon(signal_handler, tg.cancel_scope)
            await mcp.run_stdio_async()
    except CancelledError:
        print("Server shutdown complete.", file=sys.stderr)


def main() -> None:
    """
    Main entry point for the Canvas MCP Server.
    
    This function does not return as it runs the async server loop.
    """
    try:
        print("Starting Canvas MCP Server...", file=sys.stderr)
        run(run_server)
    except Exception as e:
        print(f"Error in main: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
