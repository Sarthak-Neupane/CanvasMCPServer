from datetime import datetime
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field

from ..common.untrusted_content import UntrustedContentMixin
from .assignment_summary_model import AssignmentSummary


class AssignmentCourseRef(BaseModel):
    id: Annotated[
        Optional[str],
        Field(alias="_id", description="The numeric Canvas ID of the course"),
    ] = None
    name: Annotated[
        Optional[str],
        Field(description="The name of the course"),
    ] = None


class AssignmentExternalTool(BaseModel):
    """External tool (LTI) launch or configuration metadata."""

    url: Annotated[
        Optional[str],
        Field(description="External tool launch or configuration URL"),
    ] = None
    new_tab: Annotated[
        Optional[bool],
        Field(description="Whether the external tool opens in a new browser tab"),
    ] = None
    resource_link_id: Annotated[
        Optional[str],
        Field(description="LTI resource link identifier"),
    ] = None


class AssignmentDetail(AssignmentSummary, UntrustedContentMixin):
    description: Annotated[
        Optional[str],
        Field(description="The assignment description as HTML"),
    ] = None
    unlockAt: Annotated[
        Optional[datetime],
        Field(description="The assignment is locked until this date"),
    ] = None
    lockAt: Annotated[
        Optional[datetime],
        Field(description="The assignment is locked after this date"),
    ] = None
    gradingType: Annotated[
        Optional[str],
        Field(
            description="How the assignment is graded",
            examples=["points"],
        ),
    ] = None
    submissionTypes: Annotated[
        Optional[List[str]],
        Field(
            description="Accepted submission types",
            examples=[["online_upload", "online_text_entry"]],
        ),
    ] = None
    allowedAttempts: Annotated[
        Optional[int],
        Field(
            description="Number of allowed submission attempts (null means unlimited)"
        ),
    ] = None
    course: Annotated[
        Optional[AssignmentCourseRef],
        Field(description="The course this assignment belongs to"),
    ] = None
    canvas_content_available: Annotated[
        Optional[bool],
        Field(
            description=(
                "True when instructions and content are hosted directly in Canvas; "
                "False when hosted externally (e.g. WebAssign, MindTap, Zybooks)"
            ),
        ),
    ] = None
    external_tool: Annotated[
        Optional[AssignmentExternalTool],
        Field(
            description=(
                "Metadata for third-party LTI tool when submission_types includes 'external_tool'"
            ),
        ),
    ] = None
