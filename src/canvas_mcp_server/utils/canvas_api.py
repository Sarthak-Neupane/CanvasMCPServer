"""Canvas API client utilities for making Canvas-specific requests."""

from typing import Dict, Any, Optional, List, Union, TypeVar, Type
from pydantic import BaseModel
from ..config import config
from .http_client import BaseHTTPClient, HTTPResponse, HTTPError

T = TypeVar('T', bound=BaseModel)


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
            timeout=config.get_timeout()
        )
    
    def _format_canvas_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format parameters according to Canvas API conventions.
        
        Canvas API has specific requirements for array parameters and enum values
        that need to be handled consistently across all endpoints.
        
        Args:
            params: Raw parameters dictionary
            
        Returns:
            Dict[str, Any]: Formatted parameters for Canvas API
        """
        formatted_params: Dict[str, Any] = {}
        
        for key, value in params.items():
            if value is None:
                continue
                
            # Handle array parameters that need [] suffix
            if key in ['include', 'state', 'types', 'workflow_state'] and isinstance(value, list):
                if value:  # Only add if list is not empty
                    formatted_params[f"{key}[]"] = [
                        item.value if hasattr(item, 'value') else item 
                        for item in value
                    ]
            # Handle enum values
            elif hasattr(value, 'value'):
                formatted_params[key] = value.value
            # Handle regular parameters
            else:
                formatted_params[key] = value
        
        return formatted_params
    
    async def get_canvas_data(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> HTTPResponse:
        """
        Make a GET request to Canvas API with proper parameter formatting.
        
        Args:
            endpoint: Canvas API endpoint (e.g., 'courses', 'users/self')
            params: Query parameters (will be formatted for Canvas)
            headers: Additional headers
            timeout: Request timeout
            
        Returns:
            HTTPResponse: Response from Canvas API
            
        Raises:
            HTTPError: If the request fails or Canvas returns an error
            ValueError: If configuration is invalid
        """
        # Validate configuration before making request
        config.validate()
        
        # Format parameters for Canvas API
        formatted_params = self._format_canvas_params(params or {})
        
        try:
            return await self.get(
                endpoint=endpoint,
                params=formatted_params,
                headers=headers,
                timeout=timeout
            )
        except HTTPError as e:
            # Add Canvas-specific context to errors
            if e.status_code == 401:
                raise HTTPError(
                    "Canvas API authentication failed. Please check your CANVAS_API_TOKEN.",
                    status_code=e.status_code,
                    response_data=e.response_data,
                    url=e.url
                )
            elif e.status_code == 403:
                raise HTTPError(
                    "Canvas API access forbidden. Check your permissions for this resource.",
                    status_code=e.status_code,
                    response_data=e.response_data,
                    url=e.url
                )
            elif e.status_code == 404:
                raise HTTPError(
                    f"Canvas API endpoint not found: {endpoint}",
                    status_code=e.status_code,
                    response_data=e.response_data,
                    url=e.url
                )
            else:
                # Re-raise other errors as-is
                raise
  
    async def get_paginated_data(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        max_pages: int = 10,
        per_page: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get paginated data from Canvas API.
        
        Automatically handles pagination to retrieve all results up to max_pages.
        Useful for endpoints that return large datasets.
        
        Args:
            endpoint: Canvas API endpoint
            params: Query parameters
            max_pages: Maximum number of pages to retrieve
            per_page: Number of items per page
            
        Returns:
            List[Dict[str, Any]]: Combined results from all pages
        """
        all_data: List[Dict[str, Any]] = []
        current_params = (params or {}).copy()
        current_params['per_page'] = per_page
        
        for page in range(1, max_pages + 1):
            current_params['page'] = page
            
            response = await self.get_canvas_data(endpoint, current_params)
            
            if isinstance(response.data, list):
                page_data = response.data
                all_data.extend(page_data)
                if len(page_data) < per_page:
                    break
            elif isinstance(response.data, dict):
                return [response.data]
            else:
                # If response.data is not a list or dict, return an empty list (or raise)
                return []

        
        return all_data

# Global Canvas API client instance
canvas_api_client = CanvasAPIClient()
