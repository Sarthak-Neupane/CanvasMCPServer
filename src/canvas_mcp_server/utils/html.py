"""HTML parsing helpers for Canvas content (pages, assignments, syllabi)."""

from __future__ import annotations

import re
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional

CanvasLink = Dict[str, Optional[str]]
CanvasResourceReference = Dict[str, Optional[str]]

_SKIP_CONTENT_TAGS = frozenset(
    {
        "script",
        "style",
        "noscript",
        "iframe",
        "object",
        "embed",
        "template",
        "svg",
        "canvas",
    }
)
_UNSAFE_LINK_SCHEMES = ("javascript:", "vbscript:", "data:")
_FILE_PATH_RE = re.compile(r"/courses/(?P<course_id>\d+)/files/(?P<file_id>\d+)")
_FILE_SHORT_RE = re.compile(r"/files/(?P<file_id>\d+)")
_PAGE_PATH_RE = re.compile(r"/courses/(?P<course_id>\d+)/pages/(?P<page_slug>[^/?#]+)")
_ASSIGNMENT_PATH_RE = re.compile(
    r"/courses/(?P<course_id>\d+)/assignments/(?P<assignment_id>\d+)"
)
_DISCUSSION_PATH_RE = re.compile(
    r"/courses/(?P<course_id>\d+)/discussion_topics/(?P<discussion_id>\d+)"
)
_QUIZ_PATH_RE = re.compile(r"/courses/(?P<course_id>\d+)/quizzes/(?P<quiz_id>\d+)")
_MODULE_PATH_RE = re.compile(r"/courses/(?P<course_id>\d+)/modules/(?P<module_id>\d+)")
_FOLDER_PATH_RE = re.compile(r"/courses/(?P<course_id>\d+)/folders/(?P<folder_id>\d+)")
_API_ENDPOINT_RE = re.compile(
    r'data-api-endpoint=["\'](?P<endpoint>[^"\']+)["\']',
    re.IGNORECASE,
)
_EXTERNAL_URL_RE = re.compile(r"^https?://", re.IGNORECASE)


class _TextExtractor(HTMLParser):
    """Collect visible text while skipping executable or embedded content."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._pieces: List[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: List[tuple[str, Optional[str]]]) -> None:
        if tag.lower() in _SKIP_CONTENT_TAGS:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in _SKIP_CONTENT_TAGS and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0 and data:
            self._pieces.append(data)

    def get_text(self) -> str:
        return re.sub(r"\s+", " ", "".join(self._pieces)).strip()


class _LinkExtractor(HTMLParser):
    """Extract safe anchor href/text pairs from HTML."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: List[CanvasLink] = []
        self._current_href: Optional[str] = None
        self._current_text: List[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: List[tuple[str, Optional[str]]]) -> None:
        if tag.lower() in _SKIP_CONTENT_TAGS:
            self._skip_depth += 1
            return
        if tag.lower() != "a" or self._skip_depth:
            return
        attr_map = {key.lower(): value for key, value in attrs if value is not None}
        href = attr_map.get("href")
        if href and not _is_unsafe_href(href):
            self._current_href = href
            self._current_text = []

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0 and self._current_href is not None and data:
            self._current_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in _SKIP_CONTENT_TAGS and self._skip_depth:
            self._skip_depth -= 1
            return
        if tag.lower() != "a" or self._current_href is None:
            return
        text = re.sub(r"\s+", " ", "".join(self._current_text)).strip() or None
        self.links.append({"href": self._current_href, "text": text})
        self._current_href = None
        self._current_text = []


def _is_unsafe_href(href: str) -> bool:
    normalized = href.strip().lower()
    return normalized.startswith(_UNSAFE_LINK_SCHEMES)


def html_to_text(html: Optional[str]) -> str:
    """
    Return plain text from HTML.

    Strips tags and ignores script/style/embed content. Output is for agent
    reading only — this server never executes Canvas HTML.
    """
    if not html:
        return ""
    parser = _TextExtractor()
    parser.feed(html)
    parser.close()
    return parser.get_text()


def extract_canvas_links(html: Optional[str]) -> List[CanvasLink]:
    """
    Extract anchor links from HTML.

    Returns:
        List of dicts with ``href`` and optional ``text``.
    """
    if not html:
        return []
    parser = _LinkExtractor()
    parser.feed(html)
    parser.close()
    return parser.links


def _resource(
    *,
    resource_type: str,
    url: str,
    resource_id: Optional[str] = None,
    course_id: Optional[str] = None,
    label: Optional[str] = None,
) -> CanvasResourceReference:
    return {
        "type": resource_type,
        "id": resource_id,
        "course_id": course_id,
        "url": url,
        "label": label,
    }


def _classify_href(
    href: str, label: Optional[str] = None
) -> Optional[CanvasResourceReference]:
    if _is_unsafe_href(href):
        return None

    for pattern, resource_type, id_key in (
        (_FILE_PATH_RE, "file", "file_id"),
        (_PAGE_PATH_RE, "page", "page_slug"),
        (_ASSIGNMENT_PATH_RE, "assignment", "assignment_id"),
        (_DISCUSSION_PATH_RE, "discussion", "discussion_id"),
        (_QUIZ_PATH_RE, "quiz", "quiz_id"),
        (_MODULE_PATH_RE, "module", "module_id"),
        (_FOLDER_PATH_RE, "folder", "folder_id"),
    ):
        match = pattern.search(href)
        if match:
            groups = match.groupdict()
            return _resource(
                resource_type=resource_type,
                url=href,
                resource_id=groups[id_key],
                course_id=groups.get("course_id"),
                label=label,
            )

    short_file = _FILE_SHORT_RE.search(href)
    if short_file:
        return _resource(
            resource_type="file",
            url=href,
            resource_id=short_file.group("file_id"),
            label=label,
        )

    if _EXTERNAL_URL_RE.match(href):
        return _resource(
            resource_type="external_url",
            url=href,
            resource_id=None,
            label=label,
        )

    return None


def _classify_api_endpoint(endpoint: str) -> Optional[CanvasResourceReference]:
    """Map Canvas ``data-api-endpoint`` values to resource references."""
    return _classify_href(endpoint)


def extract_canvas_resource_references(
    html: Optional[str],
) -> List[CanvasResourceReference]:
    """
    Extract Canvas resource references embedded in HTML.

    Detects course-relative links (files, pages, assignments, discussions,
    quizzes, modules, folders), short ``/files/:id`` paths, external URLs,
    and ``data-api-endpoint`` attributes on instructure embeds.

    Returns:
        Ordered list of dicts with keys: ``type``, ``id``, ``course_id``,
        ``url``, ``label``.
    """
    if not html:
        return []

    references: List[CanvasResourceReference] = []
    seen: set[tuple[str, str, str]] = set()

    def add_reference(reference: Optional[CanvasResourceReference]) -> None:
        if reference is None:
            return
        resource_id = reference.get("id")
        if resource_id:
            key = (
                str(reference.get("type") or ""),
                str(resource_id),
                str(reference.get("course_id") or ""),
            )
        else:
            key = (
                str(reference.get("type") or ""),
                str(reference.get("url") or ""),
                "",
            )
        if key in seen:
            return
        seen.add(key)
        references.append(reference)

    for link in extract_canvas_links(html):
        add_reference(_classify_href(link["href"] or "", link.get("text")))

    for match in _API_ENDPOINT_RE.finditer(html):
        add_reference(_classify_api_endpoint(match.group("endpoint")))

    return references
