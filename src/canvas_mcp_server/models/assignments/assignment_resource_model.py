from enum import Enum
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field


class AssignmentResourceType(str, Enum):
    """Canvas resource types discoverable in assignment description HTML."""

    FILE = "file"
    PAGE = "page"
    EXTERNAL_URL = "external_url"
    ASSIGNMENT = "assignment"
    DISCUSSION = "discussion"
    QUIZ = "quiz"
    MODULE = "module"
    FOLDER = "folder"


class AssignmentResource(BaseModel):
    """A linked Canvas resource embedded in an assignment description."""

    type: Annotated[
        AssignmentResourceType,
        Field(description="Resource kind (file, page, external_url, etc.)"),
    ]
    id: Annotated[
        Optional[str],
        Field(
            description=(
                "Numeric Canvas id for most types; page url slug for pages"
            ),
        ),
    ] = None
    course_id: Annotated[
        Optional[str],
        Field(description="Owning course id when known from the link"),
    ] = None
    url: Annotated[
        str,
        Field(description="Original href or API endpoint from the HTML"),
    ]
    label: Annotated[
        Optional[str],
        Field(description="Link text when extracted from an anchor tag"),
    ] = None


class AssignmentResources(BaseModel):
    """Resources linked from one assignment's description HTML."""

    course_id: Annotated[str, Field(description="The course id")]
    assignment_id: Annotated[str, Field(description="The assignment id")]
    assignment_name: Annotated[
        Optional[str],
        Field(description="Assignment display name from Canvas"),
    ] = None
    resources: Annotated[
        List[AssignmentResource],
        Field(
            description=(
                "Deduped linked resources from the description "
                "(files, pages, external URLs, etc.)"
            ),
        ),
    ]
