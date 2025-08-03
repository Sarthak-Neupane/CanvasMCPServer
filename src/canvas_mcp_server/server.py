"""Main Canvas MCP Server implementation."""

import os
import signal
import sys
from typing import List, Optional
from asyncio import CancelledError

from anyio import create_task_group, open_signal_receiver, run
from anyio.abc import CancelScope
from mcp.server.fastmcp import FastMCP

from .tools import hello_world_tool


async def signal_handler(scope: CancelScope):
    """
    Handle SIGINT and SIGTERM signals asynchronously.

    The anyio.open_signal_receiver returns an async generator that yields signal numbers
    whenever a specified signal is received. The async for loop waits for signals and processes
    them as they arrive.
    """
    with open_signal_receiver(signal.SIGINT, signal.SIGTERM) as signals:
        async for _ in signals:  # shutting down regardless of the signal type
            print("Received termination signal, shutting down gracefully...", file=sys.stderr)
            # Force immediate exit since the MCP blocks on stdio
            scope.cancel()
            return


async def run_server():
    """Run the MCP server with signal handling."""
    mcp = FastMCP(
        name="CanvasMCPServer",
        instructions="Canvas MCP Server - A Model Context Protocol server for Canvas tools",
    )

    # Register tools
    tools = [hello_world_tool]
    for tool in tools:
        mcp.add_tool(tool.fn, tool.name, tool.description, tool.annotations)

    # Register prompts (empty for now)
    prompts = []
    for prompt in prompts:
        mcp.add_prompt(prompt)

    try:
        async with create_task_group() as tg:
            tg.start_soon(signal_handler, tg.cancel_scope)
            await mcp.run_stdio_async()
    except CancelledError:
        print("Server shutdown complete.", file=sys.stderr)


def main():
    """Main entry point for the Canvas MCP Server."""
    try:
        print("Starting Canvas MCP Server...", file=sys.stderr)
        run(run_server)
    except Exception as e:
        print(f"Error in main: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)


if __name__ == "__main__":
    main()
