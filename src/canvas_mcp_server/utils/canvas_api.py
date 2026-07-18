"""Canvas API client utilities for making Canvas-specific requests."""

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
