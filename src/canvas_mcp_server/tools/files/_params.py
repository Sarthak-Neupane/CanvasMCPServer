"""Shared helpers for Canvas file listing tools."""

from typing import Any, Dict, List, Optional, Union

# Friendly aliases mapped to MIME types / lists
CONTENT_TYPE_ALIASES: Dict[str, Union[str, List[str]]] = {
    "pdf": "application/pdf",
    "image": [
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "image/svg+xml",
    ],
    "presentation": [
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/pdf",
    ],
    "spreadsheet": [
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/csv",
    ],
    "document": [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/rtf",
        "text/plain",
    ],
    "text": [
        "text/plain",
        "text/markdown",
        "text/csv",
        "text/html",
    ],
    "video": [
        "video/mp4",
        "video/quicktime",
        "video/webm",
    ],
    "audio": [
        "audio/mpeg",
        "audio/wav",
        "audio/ogg",
    ],
    "zip": [
        "application/zip",
        "application/x-zip-compressed",
    ],
}


def normalize_content_type(
    content_type: Optional[str],
) -> Optional[Union[str, List[str]]]:
    """Normalize a human-friendly alias or MIME type to Canvas-compatible content_types[]."""
    if not content_type:
        return None
    normalized = content_type.strip().lower()
    return CONTENT_TYPE_ALIASES.get(normalized, content_type)


def build_file_list_params(
    search_term: Optional[str] = None,
    content_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Build query params for Canvas list-files endpoints."""
    params: Dict[str, Any] = {"per_page": 100}
    if search_term:
        params["search_term"] = search_term
    if content_type:
        resolved = normalize_content_type(content_type)
        if resolved is not None:
            params["content_types[]"] = resolved
    return params
