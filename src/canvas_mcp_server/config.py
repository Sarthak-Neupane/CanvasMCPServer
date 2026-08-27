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
    CANVAS_DOWNLOAD_DIR: str = os.getenv(
        "CANVAS_DOWNLOAD_DIR", str(Path.home() / "Downloads" / "Canvas")
    )
    CANVAS_DOWNLOAD_TIMEOUT: int = int(
        os.getenv("CANVAS_DOWNLOAD_TIMEOUT", os.getenv("CANVAS_TIMEOUT", "30"))
    )
    CANVAS_MAX_DOWNLOAD_SIZE_MB: int = int(
        os.getenv("CANVAS_MAX_DOWNLOAD_SIZE_MB", "100")
    )
    CANVAS_MAX_RETRIES: int = int(os.getenv("CANVAS_MAX_RETRIES", "3"))
    CANVAS_RETRY_BASE_DELAY: float = float(
        os.getenv("CANVAS_RETRY_BASE_DELAY", "1.0")
    )
    
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

    @classmethod
    def get_download_dir(cls) -> Path:
        """
        Get the resolved absolute path for local Canvas downloads.

        Returns:
            Path: Expanded, absolute download root directory.
        """
        return Path(cls.CANVAS_DOWNLOAD_DIR).expanduser().resolve()

    @classmethod
    def get_download_timeout(cls) -> float:
        """
        Get timeout for binary file download requests.

        Returns:
            float: Timeout value in seconds.
        """
        return float(cls.CANVAS_DOWNLOAD_TIMEOUT)

    @classmethod
    def get_max_download_bytes(cls) -> int:
        """
        Maximum allowed file download size in bytes.

        Returns:
            int: Size cap from CANVAS_MAX_DOWNLOAD_SIZE_MB.
        """
        return cls.CANVAS_MAX_DOWNLOAD_SIZE_MB * 1024 * 1024

    @classmethod
    def get_max_retries(cls) -> int:
        """Maximum number of retries after the initial HTTP attempt."""
        return cls.CANVAS_MAX_RETRIES

    @classmethod
    def get_retry_base_delay(cls) -> float:
        """Base delay in seconds for exponential HTTP retry backoff."""
        return cls.CANVAS_RETRY_BASE_DELAY

    @classmethod
    def get_download_headers(cls) -> Dict[str, str]:
        """
        Headers for binary file downloads (no JSON Content-Type).

        Returns:
            Dict[str, str]: Authorization and User-Agent only.
        """
        return {
            "Authorization": f"Bearer {cls.CANVAS_API_TOKEN}",
            "User-Agent": "Canvas-MCP-Server/0.1.0",
        }


# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    # Don't fail on import, but warn
    print(f"Configuration warning: {e}", file=sys.stderr)


config: Config = Config()
