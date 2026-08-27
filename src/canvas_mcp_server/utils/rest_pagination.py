"""Helpers for Canvas REST API Link-header pagination."""

from __future__ import annotations

from typing import Dict

DEFAULT_PER_PAGE = 100
DEFAULT_MAX_PAGES = 10


def parse_link_header(header: str) -> Dict[str, str]:
    """
    Parse an RFC 5988 Link response header into rel -> URL mappings.

    Canvas uses rel values such as current, next, prev, first, and last.
    Header name matching is case-insensitive at the call site.
    """
    links: Dict[str, str] = {}
    if not header:
        return links

    for part in header.split(","):
        section = part.strip()
        if ";" not in section:
            continue

        url_part, *params = section.split(";")
        url = url_part.strip()
        if url.startswith("<") and url.endswith(">"):
            url = url[1:-1]

        rel: str | None = None
        for param in params:
            param = param.strip()
            if param.lower().startswith("rel="):
                rel = param[4:].strip().strip('"').strip("'")
                break

        if rel:
            links[rel.lower()] = url

    return links
