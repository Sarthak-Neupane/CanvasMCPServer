"""Canvas API client utilities for making Canvas-specific requests."""

from typing import Dict, Any, Optional, List, Union, TypeVar, Type
from pydantic import BaseModel
from ..config import config
from .http_client import BaseHTTPClient, HTTPResponse, HTTPError

T = TypeVar("T", bound=BaseModel)


class CanvasAPIClient(BaseHTTPClient):
    """
    Canvas API client with Canvas-specific functionality.

    Provides a high-level interface for making Canvas API requests with proper
    authentication, parameter formatting, and response handling.
    """

    def __init__(self) -> None:
        """Initialize Canvas API client with configuration from config module."""
        super().__init__(
            base_url=config.CANVAS_BASE_URL,
            default_headers=config.get_api_headers(),
            timeout=config.get_timeout(),
        )

    async def post_graphql_query(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> HTTPResponse:
        config.validate()
        graphql_endpoint = "graphql"
        body = {"query": query, "variables": variables or {}}
        try:
            return await self.post(
                endpoint=graphql_endpoint,
                json_data=body,
                headers=headers,
                timeout=timeout,
            )
        except HTTPError as e:
            # Add Canvas-specific context to errors
            if e.status_code == 401:
                raise HTTPError(
                    "Canvas API authentication failed. Please check your CANVAS_API_TOKEN.",
                    status_code=e.status_code,
                    response_data=e.response_data,
                    url=e.url,
                )
            elif e.status_code == 403:
                raise HTTPError(
                    "Canvas API access forbidden. Check your permissions for this resource.",
                    status_code=e.status_code,
                    response_data=e.response_data,
                    url=e.url,
                )
            elif e.status_code == 404:
                raise HTTPError(
                    f"Canvas API endpoint not found",
                    status_code=e.status_code,
                    response_data=e.response_data,
                    url=e.url,
                )
            else:
                # Re-raise other errors as-is
                raise


# Global Canvas API client instance
canvas_api_client = CanvasAPIClient()
