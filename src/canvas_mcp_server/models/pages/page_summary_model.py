from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field


class PageSummary(BaseModel):
    """Summary metadata for a Canvas wiki page (REST Pages API)."""

    page_id: Annotated[
        Optional[int],
        Field(description="The numeric Canvas ID of the page"),
    ] = None
    url: Annotated[
        Optional[str],
        Field(
            description="The page slug used in Canvas URLs",
            examples=["week-1-overview"],
        ),
    ] = None
    title: Annotated[
        Optional[str],
        Field(description="The page title"),
    ] = None
    created_at: Annotated[Optional[datetime], Field()] = None
    updated_at: Annotated[Optional[datetime], Field()] = None
    published: Annotated[
        Optional[bool],
        Field(description="Whether the page is published (not draft)"),
    ] = None
    front_page: Annotated[
        Optional[bool],
        Field(description="Whether this page is the course front page"),
    ] = None
    locked_for_user: Annotated[
        Optional[bool],
        Field(description="Whether the page is locked for the caller"),
    ] = None
    lock_explanation: Annotated[
        Optional[str],
        Field(description="Why the page is locked, when applicable"),
    ] = None
