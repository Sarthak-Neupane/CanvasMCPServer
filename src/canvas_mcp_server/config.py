"""Configuration management for Canvas MCP Server."""

import os
import sys
from typing import Dict, Optional, Union
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for Canvas MCP Server."""
    
    # API Configuration
    CANVAS_API_TOKEN: str = os.getenv("CANVAS_API_TOKEN", "")
    CANVAS_BASE_URL: str = os.getenv("CANVAS_BASE_URL", "https://canvas.instructure.com/api/v1")
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
