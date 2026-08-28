"""Pydantic model for resources discovered in a Canvas wiki page."""

from typing import Annotated, List, Optional

from pydantic import BaseModel, Field

from ..assignments.assignment_resource_model import AssignmentResource


class PageResources(BaseModel):
    """Resources linked from one Canvas wiki page's body HTML."""

    status: Annotated[
        str,
        Field(
            default="ok",
            description="Outcome status: 'ok' or 'empty'",
        ),
    ] = "ok"
    empty_reason: Annotated[
        Optional[str],
        Field(
            description="Explanatory message when resources list is empty",
        ),
    ] = None
    course_id: Annotated[str, Field(description="The course id")]
    page_url: Annotated[str, Field(description="The page url slug or numeric id")]
    page_title: Annotated[
        Optional[str],
        Field(description="Page display title from Canvas"),
    ] = None
    resources: Annotated[
        List[AssignmentResource],
        Field(
            description=(
                "Deduped linked resources discovered in the page HTML "
                "(files, pages, external URLs, assignments, quizzes, etc.)"
            ),
        ),
    ]
    result_count: Annotated[
        int,
        Field(description="Number of resources discovered"),
    ] = 0
