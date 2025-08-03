"""Tests for the api_request tool."""

import pytest
from typing import Final
from unittest.mock import patch, AsyncMock
import httpx
from canvas_mcp_server.tools.api_request import make_api_request, api_request_tool


class TestApiRequestTool:
    """Test class for API request tool."""
    
    def test_api_request_tool_properties(self) -> None:
        """Test the api_request_tool has correct properties."""
        expected_name: Final[str] = "api_request"
        assert api_request_tool.name == expected_name
        assert "api request" in api_request_tool.description.lower()
        assert api_request_tool.fn == make_api_request

    @pytest.mark.asyncio
    async def test_make_api_request_missing_token(self) -> None:
        """Test API request with missing token."""
        with patch('canvas_mcp_server.tools.api_request.config') as mock_config:
            mock_config.CANVAS_API_TOKEN = ""
            mock_config.validate.side_effect = ValueError("CANVAS_API_TOKEN is required")
            
            result: str = await make_api_request("/test")
            assert "Configuration error" in result

    @pytest.mark.asyncio
    async def test_make_api_request_success(self) -> None:
        """Test successful API request."""
        mock_response: AsyncMock = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = '{"message": "success"}'
        mock_response.raise_for_status.return_value = None
        
        with patch('canvas_mcp_server.tools.api_request.config') as mock_config:
            mock_config.CANVAS_API_TOKEN = "test_token"
            mock_config.CANVAS_BASE_URL = "https://api.test.com"
            mock_config.validate.return_value = None
            mock_config.get_api_headers.return_value = {"Authorization": "Bearer test_token"}
            mock_config.get_timeout.return_value = 30.0
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
                
                result: str = await make_api_request("/test")
                
                assert "API Response from /test" in result
                assert "Status: 200" in result
                assert '{"message": "success"}' in result

    @pytest.mark.asyncio
    async def test_make_api_request_http_error(self) -> None:
        """Test API request with HTTP error."""
        mock_response: AsyncMock = AsyncMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        
        http_error: httpx.HTTPStatusError = httpx.HTTPStatusError(
            "404 Not Found", 
            request=AsyncMock(), 
            response=mock_response
        )
        
        with patch('canvas_mcp_server.tools.api_request.config') as mock_config:
            mock_config.CANVAS_API_TOKEN = "test_token"
            mock_config.CANVAS_BASE_URL = "https://api.test.com"
            mock_config.validate.return_value = None
            mock_config.get_api_headers.return_value = {"Authorization": "Bearer test_token"}
            mock_config.get_timeout.return_value = 30.0
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_client.return_value.__aenter__.return_value.get.side_effect = http_error
                
                result: str = await make_api_request("/test")
                
                assert "API error: 404" in result

    @pytest.mark.asyncio
    async def test_make_api_request_network_error(self) -> None:
        """Test API request with network error."""
        network_error: httpx.RequestError = httpx.RequestError("Connection failed")
        
        with patch('canvas_mcp_server.tools.api_request.config') as mock_config:
            mock_config.CANVAS_API_TOKEN = "test_token"
            mock_config.CANVAS_BASE_URL = "https://api.test.com"
            mock_config.validate.return_value = None
            mock_config.get_api_headers.return_value = {"Authorization": "Bearer test_token"}
            mock_config.get_timeout.return_value = 30.0
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_client.return_value.__aenter__.return_value.get.side_effect = network_error
                
                result: str = await make_api_request("/test")
                
                assert "Request error" in result
