#!/usr/bin/env python3
"""Development server runner script."""

import sys
import os

# Add the src directory to the Python path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from canvas_mcp_server.server import main

if __name__ == "__main__":
    main()
