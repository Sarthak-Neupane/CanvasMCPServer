"""Shared helpers for Canvas file listing tools."""

from typing import Any, Dict, Optional


def build_file_list_params(
    search_term: Optional[str] = None,
    content_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Build query params for Canvas list-files endpoints."""
    params: Dict[str, Any] = {"per_page": 100}
    if search_term:
        params["search_term"] = search_term
    if content_type:
        params["content_types[]"] = content_type
    return params
