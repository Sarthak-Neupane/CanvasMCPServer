from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field


class FolderSummary(BaseModel):
    """Summary metadata for a Canvas folder (REST Folders API)."""

    id: Annotated[int, Field(description="The numeric Canvas ID of the folder")]
    name: Annotated[
        Optional[str],
        Field(description="The folder name"),
    ] = None
    full_name: Annotated[
        Optional[str],
        Field(description="Full path name, e.g. 'course files/Week 4'"),
    ] = None
    parent_folder_id: Annotated[
        Optional[int],
        Field(description="ID of the parent folder"),
    ] = None
    context_type: Annotated[
        Optional[str],
        Field(description="Course, User, or Group", examples=["Course"]),
    ] = None
    context_id: Annotated[
        Optional[int],
        Field(description="ID of the folder's context"),
    ] = None
    files_count: Annotated[
        Optional[int],
        Field(description="Number of files directly in this folder"),
    ] = None
    folders_count: Annotated[
        Optional[int],
        Field(description="Number of subfolders directly in this folder"),
    ] = None
    position: Annotated[Optional[int], Field()] = None
    created_at: Annotated[Optional[datetime], Field()] = None
    updated_at: Annotated[Optional[datetime], Field()] = None
    unlock_at: Annotated[Optional[datetime], Field()] = None
    lock_at: Annotated[Optional[datetime], Field()] = None
    locked: Annotated[Optional[bool], Field()] = None
    locked_for_user: Annotated[Optional[bool], Field()] = None
    hidden: Annotated[Optional[bool], Field()] = None
    hidden_for_user: Annotated[Optional[bool], Field()] = None
    for_submissions: Annotated[
        Optional[bool],
        Field(
            description=("True when this is a read-only submissions folder"),
        ),
    ] = None
    files_url: Annotated[
        Optional[str],
        Field(description="REST URL to list files in this folder"),
    ] = None
    folders_url: Annotated[
        Optional[str],
        Field(description="REST URL to list subfolders"),
    ] = None
