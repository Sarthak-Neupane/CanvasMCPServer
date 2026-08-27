"""Configuration management for Canvas MCP Server."""

import os
import sys
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv

# Load .env from the project root (two levels above this file), independent
# of the launcher's working directory. Falls back to cwd-based lookup.
_PROJECT_ROOT_ENV = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_PROJECT_ROOT_ENV if _PROJECT_ROOT_ENV.exists() else None)


class Config:
    """Configuration class for Canvas MCP Server."""
    
    # API Configuration
    # The base URL must end at /api (the GraphQL endpoint is {base}/graphql).
    # There is no default: the public canvas.instructure.com instance
    # (Free-for-Teacher) was permanently discontinued in 2026, so users
    # must point at their institution's Canvas domain.
    CANVAS_API_TOKEN: str = os.getenv("CANVAS_API_TOKEN", "")
    CANVAS_BASE_URL: str = os.getenv("CANVAS_BASE_URL", "")
    CANVAS_TIMEOUT: int = int(os.getenv("CANVAS_TIMEOUT", "30"))
    
    # Debug Configuration
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> None:
        """
        Validate required configuration.
        
        Raises:
            ValueError: If required configuration is missing.
        """
        if not cls.CANVAS_API_TOKEN:
            raise ValueError(
                "CANVAS_API_TOKEN is required. Please set it in your environment or .env file."
            )
        if not cls.CANVAS_BASE_URL:
            raise ValueError(
                "CANVAS_BASE_URL is required (e.g. https://your-school.instructure.com/api). "
                "Please set it in your environment or .env file."
            )
    
    @classmethod
    def get_api_headers(cls) -> Dict[str, str]:
        """
        Get headers for API requests.
        
        Returns:
            Dict[str, str]: Dictionary of HTTP headers for API requests.
        """
        return {
            "Authorization": f"Bearer {cls.CANVAS_API_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "Canvas-MCP-Server/0.1.0"
        }

    @classmethod
    def get_timeout(cls) -> float:
        """
        Get API timeout value.
        
        Returns:
            float: Timeout value in seconds.
        """
        return float(cls.CANVAS_TIMEOUT)


# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    # Don't fail on import, but warn
    print(f"Configuration warning: {e}", file=sys.stderr)


config: Config = Config()
