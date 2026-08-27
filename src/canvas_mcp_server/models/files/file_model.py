from datetime import datetime
from typing import Annotated, Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class FileSummary(BaseModel):
    """Summary metadata for a Canvas file (REST Files API)."""

    model_config = ConfigDict(populate_by_name=True)

    id: Annotated[int, Field(description="The numeric Canvas ID of the file")]
    folder_id: Annotated[
        Optional[int],
        Field(description="The folder containing this file"),
    ] = None
    display_name: Annotated[
        Optional[str],
        Field(description="The name shown for the file in Canvas"),
    ] = None
    filename: Annotated[
        Optional[str],
        Field(description="The stored filename"),
    ] = None
    content_type: Annotated[
        Optional[str],
        Field(
            alias="content-type",
            description="MIME type of the file",
            examples=["application/pdf"],
        ),
    ] = None
    url: Annotated[
        Optional[str],
        Field(description="Authenticated download URL for the file"),
    ] = None
    size: Annotated[
        Optional[int],
        Field(description="File size in bytes"),
    ] = None
    created_at: Annotated[Optional[datetime], Field()] = None
    updated_at: Annotated[Optional[datetime], Field()] = None
    modified_at: Annotated[Optional[datetime], Field()] = None
    mime_class: Annotated[
        Optional[str],
        Field(description="Simplified MIME category", examples=["pdf", "doc"]),
    ] = None
    locked: Annotated[Optional[bool], Field()] = None
    hidden: Annotated[Optional[bool], Field()] = None
    hidden_for_user: Annotated[Optional[bool], Field()] = None
    locked_for_user: Annotated[Optional[bool], Field()] = None
    visibility_level: Annotated[
        Optional[str],
        Field(description="inherit, course, institution, or public"),
    ] = None


class FileDetail(FileSummary):
    """Full file metadata including lock details."""

    unlock_at: Annotated[Optional[datetime], Field()] = None
    lock_at: Annotated[Optional[datetime], Field()] = None
    lock_explanation: Annotated[
        Optional[str],
        Field(description="Why the file is locked for the caller"),
    ] = None
    lock_info: Annotated[
        Optional[Dict[str, Any]],
        Field(description="Structured lock metadata from Canvas"),
    ] = None
    thumbnail_url: Annotated[Optional[str], Field()] = None
    preview_url: Annotated[
        Optional[str],
        Field(description="Document preview URL when available"),
    ] = None
    media_entry_id: Annotated[Optional[str], Field()] = None
    category: Annotated[Optional[str], Field()] = None
