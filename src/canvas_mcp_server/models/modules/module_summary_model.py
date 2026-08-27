from datetime import datetime
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field


class ModuleSummary(BaseModel):
    """Structure-only summary of a Canvas course module (no nested items)."""

    id: Annotated[int, Field(description="The numeric Canvas ID of the module")]
    name: Annotated[
        Optional[str],
        Field(description="The module name", examples=["Week 4"]),
    ] = None
    position: Annotated[
        Optional[int],
        Field(description="1-based position of this module in the course"),
    ] = None
    unlock_at: Annotated[
        Optional[datetime],
        Field(description="When this module unlocks, if set"),
    ] = None
    require_sequential_progress: Annotated[
        Optional[bool],
        Field(description="Whether module items must be unlocked in order"),
    ] = None
    requirement_type: Annotated[
        Optional[str],
        Field(
            description="Whether all or one required items must be completed",
            examples=["all", "one"],
        ),
    ] = None
    prerequisite_module_ids: Annotated[
        Optional[List[int]],
        Field(description="IDs of modules that must be completed first"),
    ] = None
    items_count: Annotated[
        Optional[int],
        Field(description="Number of items in the module"),
    ] = None
    workflow_state: Annotated[
        Optional[str],
        Field(description="Module workflow state", examples=["active", "deleted"]),
    ] = None
    state: Annotated[
        Optional[str],
        Field(
            description=(
                "Progression state for the calling student: "
                "locked, unlocked, started, or completed"
            ),
            examples=["started"],
        ),
    ] = None
    completed_at: Annotated[
        Optional[datetime],
        Field(description="When the calling student completed this module, if any"),
    ] = None
    published: Annotated[
        Optional[bool],
        Field(
            description=(
                "Whether the module is published "
                "(present only when the caller can view unpublished modules)"
            ),
        ),
    ] = None
