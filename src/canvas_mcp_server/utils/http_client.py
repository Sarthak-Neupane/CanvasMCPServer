"""HTTP client utilities for making API requests."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import httpx

from ..config import config
from .redaction import redact_sensitive_text, redact_url
from .retry_policy import (
    compute_retry_delay,
    should_retry_status,
    sleep_before_retry,
)


@dataclass
class HTTPResponse:
    """
    Standardized HTTP response wrapper.

    Provides a consistent interface for HTTP responses across all API calls,
    making it easier to handle responses in a uniform way.
    """

    status_code: int
    data: Union[Dict[str, Any], List[Any], str]
    headers: Dict[str, str]
    url: str

    @property
    def is_success(self) -> bool:
        """Check if the response indicates success (2xx status code)."""
        return 200 <= self.status_code < 300

    @property
    def is_client_error(self) -> bool:
        """Check if the response indicates client error (4xx status code)."""
        return 400 <= self.status_code < 500

    @property
    def is_server_error(self) -> bool:
        """Check if the response indicates server error (5xx status code)."""
        return 500 <= self.status_code < 600


class HTTPError(Exception):
    """
    Custom exception for HTTP-related errors.

    Provides detailed error information including status codes, response data,
    and request context for better debugging and error handling.
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Union[Dict[str, Any], str]] = None,
        url: Optional[str] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data
        self.url = url

    def __str__(self) -> str:
        """Provide detailed error information for debugging."""
        base_msg = redact_sensitive_text(super().__str__())
        if self.status_code:
            base_msg += f" (Status: {self.status_code})"
        if self.url:
            safe_url = redact_url(self.url)
            if safe_url:
                base_msg += f" (URL: {safe_url})"
        return base_msg


class BaseHTTPClient:
    """
    Base HTTP client with common functionality.

    Provides a foundation for creating API-specific clients with shared
    functionality like timeout handling, header management, and error processing.
    """

    def __init__(
        self,
        base_url: str,
        default_headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.default_headers = default_headers or {}
        self.timeout = timeout
        self._http_client: Optional[httpx.AsyncClient] = None

    def _build_url(self, endpoint: str) -> str:
        """Build full URL from base URL and endpoint."""
        endpoint = endpoint.lstrip("/")
        return f"{self.base_url}/{endpoint}"

    def _merge_headers(
        self, additional_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """Merge default headers with additional headers."""
        headers = self.default_headers.copy()
        if additional_headers:
            headers.update(additional_headers)
        return headers

    def _http_response_from_httpx(
        self,
        response: httpx.Response,
        *,
        url: str,
        raise_on_error: bool = True,
    ) -> HTTPResponse:
        """Convert an httpx response into the shared HTTPResponse wrapper."""
        try:
            response_data = response.json()
        except (ValueError, httpx.InvalidURL):
            response_data = response.text

        http_response = HTTPResponse(
            status_code=response.status_code,
            data=response_data,
            headers=dict(response.headers),
            url=str(response.url),
        )

        if not http_response.is_success and raise_on_error:
            error_msg = f"HTTP {response.status_code} error"
            if isinstance(response_data, dict) and "message" in response_data:
                error_msg += f": {response_data['message']}"
            elif isinstance(response_data, str):
                error_msg += f": {response_data[:200]}..."

            raise HTTPError(
                message=error_msg,
                status_code=response.status_code,
                response_data=response_data,
                url=url,
            )

        return http_response

    async def _request_with_client(
        self,
        client: httpx.AsyncClient,
        method: str,
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> HTTPResponse:
        merged_headers = self._merge_headers(headers)
        request_timeout = timeout or self.timeout
        max_attempts = config.get_max_retries() + 1
        base_delay = config.get_retry_base_delay()

        for attempt in range(max_attempts):
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=merged_headers,
                    timeout=request_timeout,
                )
            except httpx.TimeoutException:
                if attempt >= max_attempts - 1:
                    raise HTTPError(
                        f"Request timeout after {request_timeout}s",
                        url=url,
                    )
                await sleep_before_retry(
                    compute_retry_delay(attempt, None, base_delay=base_delay)
                )
                continue
            except httpx.NetworkError as e:
                if attempt >= max_attempts - 1:
                    raise HTTPError(f"Network error: {str(e)}", url=url)
                await sleep_before_retry(
                    compute_retry_delay(attempt, None, base_delay=base_delay)
                )
                continue
            except httpx.HTTPStatusError as e:
                raise HTTPError(
                    f"HTTP error: {e.response.status_code}",
                    status_code=e.response.status_code,
                    url=url,
                )

            if response.is_success:
                return self._http_response_from_httpx(
                    response,
                    url=url,
                    raise_on_error=True,
                )

            if should_retry_status(response.status_code) and attempt < max_attempts - 1:
                await sleep_before_retry(
                    compute_retry_delay(
                        attempt,
                        response.headers.get("Retry-After"),
                        base_delay=base_delay,
                    )
                )
                continue

            return self._http_response_from_httpx(
                response,
                url=url,
                raise_on_error=True,
            )

        raise HTTPError("Request failed after retries", url=url)

    async def _send_request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> HTTPResponse:
        """Send one HTTP request using the shared client when available."""
        request_timeout = timeout or self.timeout

        if self._http_client is not None:
            return await self._request_with_client(
                self._http_client,
                method,
                url,
                params=params,
                json_data=json_data,
                headers=headers,
                timeout=timeout,
            )

        async with httpx.AsyncClient(timeout=request_timeout) as client:
            return await self._request_with_client(
                client,
                method,
                url,
                params=params,
                json_data=json_data,
                headers=headers,
                timeout=timeout,
            )

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> HTTPResponse:
        """
        Make an HTTP request with standardized error handling.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (relative to base_url)
            params: Query parameters
            json_data: JSON body data
            headers: Additional headers
            timeout: Request timeout (uses default if not specified)

        Returns:
            HTTPResponse: Standardized response object

        Raises:
            HTTPError: If the request fails or returns an error status
        """
        url = self._build_url(endpoint)
        return await self._send_request(
            method,
            url,
            params=params,
            json_data=json_data,
            headers=headers,
            timeout=timeout,
        )

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> HTTPResponse:
        """Make a GET request."""
        return await self._make_request(
            "GET", endpoint, params=params, headers=headers, timeout=timeout
        )

    async def get_absolute(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> HTTPResponse:
        """
        Make a GET request to a fully qualified URL.

        Used to follow opaque Canvas pagination links from the Link header.
        """
        return await self._send_request(
            "GET",
            url,
            headers=headers,
            timeout=timeout,
        )

    async def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> HTTPResponse:
        """Make a POST request."""
        return await self._make_request(
            "POST",
            endpoint,
            params=params,
            json_data=json_data,
            headers=headers,
            timeout=timeout,
        )

    async def put(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> HTTPResponse:
        """Make a PUT request."""
        return await self._make_request(
            "PUT",
            endpoint,
            params=params,
            json_data=json_data,
            headers=headers,
            timeout=timeout,
        )

    async def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> HTTPResponse:
        """Make a DELETE request."""
        return await self._make_request(
            "DELETE", endpoint, params=params, headers=headers, timeout=timeout
        )

    async def patch(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> HTTPResponse:
        """Make a PATCH request."""
        return await self._make_request(
            "PATCH",
            endpoint,
            params=params,
            json_data=json_data,
            headers=headers,
            timeout=timeout,
        )
