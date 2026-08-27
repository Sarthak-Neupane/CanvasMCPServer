"""Internal types for course content search."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Final, List, Optional

SEARCH_CONTENT_TYPES: Final[List[str]] = [
    "syllabus",
    "page",
    "assignment",
    "module",
    "announcement",
    "file",
    "quiz",
    "discussion",
]


@dataclass
class SearchDocument:
    """Normalized searchable item before ranking."""

    content_type: str
    title: str
    body: str
    course_id: str
    resource_id: Optional[str]
    url: Optional[str]
    updated_at: Optional[datetime] = None
