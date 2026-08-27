from datetime import datetime
from typing import Annotated, Any, Dict, Optional

from pydantic import BaseModel, Field


class CompletionRequirement(BaseModel):
    type: Annotated[
        Optional[str],
        Field(
            description=(
                "must_view, must_submit, must_contribute, min_score, "
                "min_percentage, or must_mark_done"
            ),
            examples=["must_view"],
        ),
    ] = None
    min_score: Annotated[
        Optional[float],
        Field(description="Minimum score required when type is min_score"),
    ] = None
    min_percentage: Annotated[
        Optional[float],
        Field(description="Minimum percentage required when type is min_percentage"),
    ] = None
    completed: Annotated[
        Optional[bool],
        Field(
            description=(
                "Whether the calling student has met this requirement "
                "(present for students)"
            ),
        ),
    ] = None


class ContentDetails(BaseModel):
    points_possible: Annotated[
        Optional[float],
        Field(description="Points possible for the linked content, if applicable"),
    ] = None
    due_at: Annotated[
        Optional[datetime],
        Field(description="Due date of the linked content, if applicable"),
    ] = None
    unlock_at: Annotated[
        Optional[datetime],
        Field(description="Unlock date of the linked content, if applicable"),
    ] = None
    lock_at: Annotated[
        Optional[datetime],
        Field(description="Lock date of the linked content, if applicable"),
    ] = None
    locked_for_user: Annotated[
        Optional[bool],
        Field(description="Whether the linked content is locked for the caller"),
    ] = None
    lock_explanation: Annotated[
        Optional[str],
        Field(description="Human-readable explanation of why the content is locked"),
    ] = None
    lock_info: Annotated[
        Optional[Dict[str, Any]],
        Field(description="Structured lock metadata from Canvas, if present"),
    ] = None


class ModuleItemSummary(BaseModel):
    """Lean module item inventory entry (no content_details)."""

    id: Annotated[int, Field(description="The numeric Canvas ID of the module item")]
    module_id: Annotated[
        Optional[int],
        Field(description="The module this item belongs to"),
    ] = None
    position: Annotated[
        Optional[int],
        Field(description="1-based position of this item in the module"),
    ] = None
    title: Annotated[
        Optional[str],
        Field(description="The item title"),
    ] = None
    indent: Annotated[
        Optional[int],
        Field(description="0-based indent level for hierarchy display"),
    ] = None
    type: Annotated[
        Optional[str],
        Field(
            description=(
                "File, Page, Discussion, Assignment, Quiz, SubHeader, "
                "ExternalUrl, or ExternalTool"
            ),
            examples=["Assignment"],
        ),
    ] = None
    content_id: Annotated[
        Optional[int],
        Field(
            description=(
                "ID of the linked object (File, Discussion, Assignment, "
                "Quiz, ExternalTool)"
            ),
        ),
    ] = None
    html_url: Annotated[
        Optional[str],
        Field(description="Link to the item in the Canvas web UI"),
    ] = None
    url: Annotated[
        Optional[str],
        Field(description="Canvas API URL for the linked object, if applicable"),
    ] = None
    page_url: Annotated[
        Optional[str],
        Field(description="Wiki page locator (Page items only)"),
    ] = None
    external_url: Annotated[
        Optional[str],
        Field(description="External URL (ExternalUrl / ExternalTool items)"),
    ] = None
    new_tab: Annotated[
        Optional[bool],
        Field(description="Whether an ExternalTool opens in a new tab"),
    ] = None
    completion_requirement: Annotated[
        Optional[CompletionRequirement],
        Field(description="Completion requirement for this item, if any"),
    ] = None
    published: Annotated[
        Optional[bool],
        Field(
            description=(
                "Whether the item is published "
                "(present only when the caller can view unpublished items)"
            ),
        ),
    ] = None


class ModuleItemDetail(ModuleItemSummary):
    """Single module item including content_details when requested."""

    content_details: Annotated[
        Optional[ContentDetails],
        Field(
            description=(
                "Lock/due/points details for the linked content "
                "(from include[]=content_details)"
            ),
        ),
    ] = None
