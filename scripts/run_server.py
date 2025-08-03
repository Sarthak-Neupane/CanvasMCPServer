#!/usr/bin/env python3
"""Development server runner script."""

import sys
import os
from typing import NoReturn

# Add the src directory to the Python path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from canvas_mcp_server.server import main


def run_development_server() -> NoReturn:
    """
    Run the development server.
    
    This function does not return as it runs the server loop.
    """
    main()


if __name__ == "__main__":
    run_development_server()
