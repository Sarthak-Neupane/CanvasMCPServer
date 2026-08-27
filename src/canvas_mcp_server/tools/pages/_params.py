"""Helpers for Canvas wiki page REST endpoints."""

import re
from typing import Final

_COURSE_PAGE_PATH_RE: Final = re.compile(r"/courses/\d+/pages/(?P<slug>[^/?#]+)")


def normalize_page_locator(page_id_or_url: str) -> str:
    """
    Normalize a page slug, numeric id, or Canvas web path for the Pages API.

    Accepts values like ``week-1``, ``14``, or
    ``/courses/100001/pages/week-1``.
    """
    locator = page_id_or_url.strip()
    path_match = _COURSE_PAGE_PATH_RE.search(locator)
    if path_match:
        return path_match.group("slug")
    return locator.strip("/")


def page_endpoint_segment(page_id_or_url: str) -> str:
    """
    Build the ``:url_or_id`` path segment for GET /courses/:id/pages/:url_or_id.

    Numeric ids use the ``page_id:`` prefix so Canvas does not treat them as
    URL slugs (see Canvas Pages API docs).
    """
    locator = normalize_page_locator(page_id_or_url)
    if locator.isdigit():
        return f"page_id:{locator}"
    return locator
