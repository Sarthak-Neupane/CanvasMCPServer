"""Pydantic model for unified course search results."""

from typing import Annotated, Optional

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """One ranked hit from search_course_content."""

    content_type: Annotated[
        str,
        Field(
            description=(
                "syllabus, page, assignment, module, announcement, file, "
                "quiz, or discussion"
            ),
        ),
    ]
    title: Annotated[str, Field(description="Display title for the result")]
    snippet: Annotated[
        Optional[str],
        Field(
            description=(
                "Short excerpt around the query match (bounded, not full body)"
            ),
        ),
    ] = None
    score: Annotated[
        float,
        Field(description="Local relevance score (higher is better)"),
    ]
    course_id: Annotated[str, Field(description="Canvas course id")]
    resource_id: Annotated[
        Optional[str],
        Field(description="Primary Canvas id for the matched object"),
    ] = None
    url: Annotated[
        Optional[str],
        Field(description="Canvas web or API URL when available"),
    ] = None
    source_type: Annotated[
        Optional[str],
        Field(
            description="Same as content_type; included for unified metadata naming",
        ),
    ] = None
    canvas_url: Annotated[
        Optional[str],
        Field(
            description="Canvas web path or URL for the matched object",
        ),
    ] = None
