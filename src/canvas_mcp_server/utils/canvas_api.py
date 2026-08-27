"""Canvas API client utilities for making Canvas-specific requests."""

import httpx

from pathlib import Path
from typing import Dict, Any, Optional

from ..config import config
from .http_client import BaseHTTPClient, HTTPResponse, HTTPError


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
        """
        Execute a GraphQL query against the Canvas API.

        Posts to {CANVAS_BASE_URL}/graphql per the Canvas GraphQL docs.

        Args:
            query: The GraphQL query or mutation to execute.
            variables: Values for any variables referenced by the query.
            headers: Additional headers to merge into the request.
            timeout: Request timeout override in seconds.

        Returns:
            HTTPResponse: The raw response; GraphQL payload is in `.data`.

        Raises:
            HTTPError: If the request fails or Canvas returns an error status.
            ValueError: If required configuration (API token) is missing.
        """
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
            raise self._contextualize_error(e) from e

    async def get_rest(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> HTTPResponse:
        """
        Make a GET request to a Canvas REST endpoint.

        Used for data the GraphQL API does not expose (e.g. todo items and
        upcoming events). The endpoint is relative to {CANVAS_BASE_URL}, so
        REST paths must include the version prefix, e.g. "v1/users/self/todo".

        Args:
            endpoint: REST endpoint relative to the base URL (e.g. "v1/users/self/todo").
            params: Query parameters.
            headers: Additional headers to merge into the request.
            timeout: Request timeout override in seconds.

        Returns:
            HTTPResponse: The raw response; the JSON payload is in `.data`.

        Raises:
            HTTPError: If the request fails or Canvas returns an error status.
            ValueError: If required configuration (API token) is missing.
        """
        config.validate()
        try:
            return await self.get(
                endpoint=endpoint,
                params=params,
                headers=headers,
                timeout=timeout,
            )
        except HTTPError as e:
            raise self._contextualize_error(e) from e

    async def download_file_to_path(
        self,
        url: str,
        destination: Path,
        *,
        max_bytes: Optional[int] = None,
        timeout: Optional[float] = None,
    ) -> int:
        """
        Stream a Canvas file download to disk with a size cap.

        Args:
            url: Authenticated download URL from the Files API.
            destination: Local path to write (parent dirs are not created here).
            max_bytes: Maximum bytes to accept; defaults to config limit.
            timeout: Request timeout override in seconds.

        Returns:
            int: Number of bytes written.

        Raises:
            HTTPError: If the request fails, the file is too large, or Canvas
                returns an error status.
            ValueError: If required configuration is missing.
        """
        config.validate()
        request_timeout = timeout or config.get_download_timeout()
        byte_limit = max_bytes if max_bytes is not None else config.get_max_download_bytes()
        headers = config.get_download_headers()
        try:
            async with httpx.AsyncClient(
                timeout=request_timeout, follow_redirects=True
            ) as client:
                async with client.stream("GET", url, headers=headers) as response:
                    if not (200 <= response.status_code < 300):
                        body_preview = ""
                        async for chunk in response.aiter_bytes():
                            body_preview += chunk.decode("utf-8", errors="replace")
                            if len(body_preview) >= 500:
                                break
                        raise HTTPError(
                            f"HTTP {response.status_code} error",
                            status_code=response.status_code,
                            response_data=body_preview,
                            url=url,
                        )

                    content_length = response.headers.get("content-length")
                    if content_length is not None:
                        try:
                            declared_size = int(content_length)
                        except ValueError:
                            declared_size = None
                        if declared_size is not None and declared_size > byte_limit:
                            raise HTTPError(
                                f"File exceeds maximum download size of "
                                f"{byte_limit} bytes",
                                status_code=response.status_code,
                                url=url,
                            )

                    bytes_written = 0
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        with destination.open("wb") as handle:
                            async for chunk in response.aiter_bytes():
                                bytes_written += len(chunk)
                                if bytes_written > byte_limit:
                                    raise HTTPError(
                                        f"File exceeds maximum download size of "
                                        f"{byte_limit} bytes",
                                        status_code=response.status_code,
                                        url=url,
                                    )
                                handle.write(chunk)
                    except Exception:
                        destination.unlink(missing_ok=True)
                        raise

                    return bytes_written
        except httpx.TimeoutException:
            destination.unlink(missing_ok=True)
            raise HTTPError(
                f"Download timeout after {request_timeout}s", url=url
            ) from None
        except httpx.NetworkError as e:
            destination.unlink(missing_ok=True)
            raise HTTPError(f"Network error: {str(e)}", url=url) from e

    async def download_file_bytes(
        self,
        url: str,
        timeout: Optional[float] = None,
    ) -> bytes:
        """
        Download raw file bytes from a Canvas file URL.

        Uses Authorization only (no JSON Content-Type). Follows redirects.
        Prefer download_file_to_path for production downloads.

        Args:
            url: Authenticated download URL from the Files API.
            timeout: Request timeout override in seconds.

        Returns:
            bytes: The file body.

        Raises:
            HTTPError: If the request fails or Canvas returns an error status.
            ValueError: If required configuration is missing.
        """
        config.validate()
        request_timeout = timeout or config.get_download_timeout()
        headers = config.get_download_headers()
        try:
            async with httpx.AsyncClient(
                timeout=request_timeout, follow_redirects=True
            ) as client:
                response = await client.get(url, headers=headers)
                if not (200 <= response.status_code < 300):
                    raise HTTPError(
                        f"HTTP {response.status_code} error",
                        status_code=response.status_code,
                        response_data=response.text[:500],
                        url=url,
                    )
                return response.content
        except httpx.TimeoutException:
            raise HTTPError(
                f"Download timeout after {request_timeout}s", url=url
            ) from None
        except httpx.NetworkError as e:
            raise HTTPError(f"Network error: {str(e)}", url=url) from e

    def _contextualize_error(self, e: HTTPError) -> HTTPError:
        """Wrap common HTTP errors with Canvas-specific guidance."""
        if e.status_code == 401:
            return HTTPError(
                "Canvas API authentication failed. Please check your CANVAS_API_TOKEN.",
                status_code=e.status_code,
                response_data=e.response_data,
                url=e.url,
            )
        if e.status_code == 403:
            return HTTPError(
                "Canvas API access forbidden. Check your permissions for this resource.",
                status_code=e.status_code,
                response_data=e.response_data,
                url=e.url,
            )
        if e.status_code == 404:
            return HTTPError(
                "Canvas API endpoint not found",
                status_code=e.status_code,
                response_data=e.response_data,
                url=e.url,
            )
        if e.status_code == 429:
            return HTTPError(
                "Canvas API rate limit exceeded. Retry the request later.",
                status_code=e.status_code,
                response_data=e.response_data,
                url=e.url,
            )
        if e.status_code is not None and 500 <= e.status_code < 600:
            return HTTPError(
                "Canvas is temporarily unavailable "
                f"(HTTP {e.status_code}). This is a Canvas-side outage; "
                "retry once the platform is back up.",
                status_code=e.status_code,
                response_data=e.response_data,
                url=e.url,
            )
        return e


def extract_graphql_data(response: HTTPResponse) -> Dict[str, Any]:
    """
    Extract the `data` payload from a GraphQL response.

    Canvas returns HTTP 200 even when the query fails, with the failure
    reported in a top-level `errors` array, so both cases are handled here.

    Args:
        response: The HTTPResponse from post_graphql_query.

    Returns:
        Dict[str, Any]: The GraphQL `data` object.

    Raises:
        HTTPError: If the response is not a JSON object or contains GraphQL errors.
    """
    if not isinstance(response.data, dict):
        raise HTTPError(
            "Canvas GraphQL response was not a JSON object",
            status_code=response.status_code,
            url=response.url,
        )
    errors = response.data.get("errors")
    if errors:
        messages = "; ".join(
            str(err.get("message", err)) for err in errors if isinstance(err, dict)
        ) or str(errors)
        raise HTTPError(
            f"Canvas GraphQL error: {messages}",
            status_code=response.status_code,
            response_data=response.data,
            url=response.url,
        )
    data = response.data.get("data")
    if not isinstance(data, dict):
        raise HTTPError(
            "Canvas GraphQL response contained no data",
            status_code=response.status_code,
            response_data=response.data,
            url=response.url,
        )
    return data


# Global Canvas API client instance
canvas_api_client = CanvasAPIClient()
