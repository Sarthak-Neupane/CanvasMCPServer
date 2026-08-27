"""Mock helpers for patching the global Canvas API client in tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union
from unittest.mock import AsyncMock

from canvas_mcp_server.utils.canvas_api import canvas_api_client
from canvas_mcp_server.utils.http_client import HTTPError, HTTPResponse

RestRoute = Union[HTTPResponse, Callable[..., Any]]


def make_http_response(
    data: Union[Dict[str, Any], List[Any], str],
    *,
    status_code: int = 200,
    url: str = "https://canvas.example.edu/api/v1/mock",
    headers: Optional[Dict[str, str]] = None,
) -> HTTPResponse:
    """Build an HTTPResponse the same way production code expects."""
    return HTTPResponse(
        status_code=status_code,
        data=data,
        headers=headers or {},
        url=url,
    )


def make_graphql_response(
    data: Dict[str, Any],
    *,
    url: str = "https://canvas.example.edu/api/graphql",
) -> HTTPResponse:
    """Wrap GraphQL `data` in the HTTP envelope Canvas returns."""
    return make_http_response({"data": data}, url=url)


@dataclass
class CanvasAPIMock:
    """
    Patches canvas_api_client REST/GraphQL/download methods for a test.

    Usage:
        async def test_foo(canvas_api: CanvasAPIMock):
            canvas_api.rest_returns("v1/courses", [...])
            canvas_api.graphql_returns({"allCourses": [...]})
            ...
    """

    graphql: AsyncMock = field(default_factory=AsyncMock)
    rest: AsyncMock = field(default_factory=AsyncMock)
    download: AsyncMock = field(default_factory=AsyncMock)
    _rest_routes: Dict[str, RestRoute] = field(default_factory=dict)
    _graphql_queue: List[HTTPResponse] = field(default_factory=list)

    def _match_rest_route(self, endpoint: str) -> Optional[RestRoute]:
        if endpoint in self._rest_routes:
            return self._rest_routes[endpoint]
        for prefix in sorted(self._rest_routes, key=len, reverse=True):
            if endpoint.startswith(prefix):
                return self._rest_routes[prefix]
        return None

    def configure(self) -> None:
        """Wire AsyncMocks to route-based handlers."""

        async def _rest_handler(
            endpoint: str,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            timeout: Optional[float] = None,
        ) -> HTTPResponse:
            route = self._match_rest_route(endpoint)
            if route is None:
                raise HTTPError(
                    f"No REST mock registered for endpoint: {endpoint}",
                    status_code=404,
                    url=endpoint,
                )
            if callable(route):
                return await route(
                    endpoint,
                    params=params,
                    headers=headers,
                    timeout=timeout,
                )
            return route

        async def _graphql_handler(
            query: str,
            variables: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            timeout: Optional[float] = None,
        ) -> HTTPResponse:
            del query, variables, headers, timeout
            if not self._graphql_queue:
                raise HTTPError(
                    "No GraphQL mock registered",
                    status_code=500,
                    url="graphql",
                )
            return self._graphql_queue.pop(0)

        self.rest.side_effect = _rest_handler
        self.graphql.side_effect = _graphql_handler

    def rest_returns(
        self,
        endpoint: str,
        data: Union[Dict[str, Any], List[Any], str],
        *,
        status_code: int = 200,
        url: Optional[str] = None,
    ) -> "CanvasAPIMock":
        """Register a REST response for an endpoint (exact or prefix match)."""
        self._rest_routes[endpoint] = make_http_response(
            data,
            status_code=status_code,
            url=url or f"https://canvas.example.edu/api/{endpoint}",
        )
        return self

    def graphql_returns(
        self,
        data: Dict[str, Any],
        *,
        url: Optional[str] = None,
    ) -> "CanvasAPIMock":
        """Queue a GraphQL success response (popped in call order)."""
        self._graphql_queue.append(
            make_graphql_response(data, url=url or "https://canvas.example.edu/api/graphql")
        )
        return self

    def graphql_error(
        self,
        message: str = "GraphQL error",
        *,
        url: Optional[str] = None,
    ) -> "CanvasAPIMock":
        """Queue a GraphQL error envelope."""
        self._graphql_queue.append(
            make_http_response(
                {"errors": [{"message": message}]},
                url=url or "https://canvas.example.edu/api/graphql",
            )
        )
        return self

    def rest_error(
        self,
        endpoint: str,
        *,
        status_code: int = 403,
        message: str = "Forbidden",
    ) -> "CanvasAPIMock":
        """Register a REST endpoint that raises HTTPError."""

        async def _raise(*_args: Any, **_kwargs: Any) -> HTTPResponse:
            raise HTTPError(
                message,
                status_code=status_code,
                url=f"https://canvas.example.edu/api/{endpoint}",
            )

        self._rest_routes[endpoint] = _raise
        return self

    def apply(self) -> "CanvasAPIMock":
        """Patch the global client and return self."""
        self.configure()
        canvas_api_client.post_graphql_query = self.graphql
        canvas_api_client.get_rest = self.rest
        canvas_api_client.download_file_bytes = self.download
        return self
