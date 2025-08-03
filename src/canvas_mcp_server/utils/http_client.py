"""HTTP client utilities for making API requests."""

from typing import Dict, Any, Optional, Union, TypeVar, Generic
from dataclasses import dataclass
import httpx
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


@dataclass
class HTTPResponse:
    """
    Standardized HTTP response wrapper.
    
    Provides a consistent interface for HTTP responses across all API calls,
    making it easier to handle responses in a uniform way.
    """
    
    status_code: int
    data: Union[Dict[str, Any], list, str]
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
        url: Optional[str] = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data
        self.url = url
    
    def __str__(self) -> str:
        """Provide detailed error information for debugging."""
        base_msg = super().__str__()
        if self.status_code:
            base_msg += f" (Status: {self.status_code})"
        if self.url:
            base_msg += f" (URL: {self.url})"
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
        timeout: float = 30.0
    ):
        self.base_url = base_url.rstrip('/')
        self.default_headers = default_headers or {}
        self.timeout = timeout
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from base URL and endpoint."""
        endpoint = endpoint.lstrip('/')
        return f"{self.base_url}/{endpoint}"
    
    def _merge_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Merge default headers with additional headers."""
        headers = self.default_headers.copy()
        if additional_headers:
            headers.update(additional_headers)
        return headers
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
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
        merged_headers = self._merge_headers(headers)
        request_timeout = timeout or self.timeout
        
        try:
            async with httpx.AsyncClient(timeout=request_timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=merged_headers
                )
                
                # Parse response data
                try:
                    response_data = response.json()
                except (ValueError, httpx.InvalidURL):
                    response_data = response.text
                
                # Create standardized response
                http_response = HTTPResponse(
                    status_code=response.status_code,
                    data=response_data,
                    headers=dict(response.headers),
                    url=str(response.url)
                )
                
                # Raise exception for error status codes
                if not http_response.is_success:
                    error_msg = f"HTTP {response.status_code} error"
                    if isinstance(response_data, dict) and 'message' in response_data:
                        error_msg += f": {response_data['message']}"
                    elif isinstance(response_data, str):
                        error_msg += f": {response_data[:200]}..."
                    
                    raise HTTPError(
                        message=error_msg,
                        status_code=response.status_code,
                        response_data=response_data,
                        url=url
                    )
                
                return http_response
                
        except httpx.TimeoutException:
            raise HTTPError(f"Request timeout after {request_timeout}s", url=url)
        except httpx.NetworkError as e:
            raise HTTPError(f"Network error: {str(e)}", url=url)
        except httpx.HTTPStatusError as e:
            # This shouldn't happen since we handle status codes above,
            # but included for completeness
            raise HTTPError(
                f"HTTP error: {e.response.status_code}",
                status_code=e.response.status_code,
                url=url
            )
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> HTTPResponse:
        """Make a GET request."""
        return await self._make_request("GET", endpoint, params=params, headers=headers, timeout=timeout)
    
    async def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> HTTPResponse:
        """Make a POST request."""
        return await self._make_request("POST", endpoint, params=params, json_data=json_data, headers=headers, timeout=timeout)
    
    async def put(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> HTTPResponse:
        """Make a PUT request."""
        return await self._make_request("PUT", endpoint, params=params, json_data=json_data, headers=headers, timeout=timeout)
    
    async def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> HTTPResponse:
        """Make a DELETE request."""
        return await self._make_request("DELETE", endpoint, params=params, headers=headers, timeout=timeout)
    
    async def patch(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> HTTPResponse:
        """Make a PATCH request."""
        return await self._make_request("PATCH", endpoint, params=params, json_data=json_data, headers=headers, timeout=timeout)
