"""Tool for unified course content search."""

from typing import Final, List, Dict, Any, Optional, Union, TypeAlias, Annotated

from mcp.server.fastmcp.tools import Tool
from pydantic import Field

from ...errors import as_tool_error
from ...models import ListResult, SearchResult
from ...utils.list_results import list_result
from ._rank import rank_documents
from ._snippet import make_snippet
from ._sources import collect_search_documents
from ._types import SEARCH_CONTENT_TYPES

SearchResultsResponse: TypeAlias = Union[ListResult[SearchResult], Dict[str, Any]]


async def search_course_content(
    course_id: Annotated[
        str,
        Field(description="The course ID (numeric Canvas ID, e.g. '182571')."),
    ],
    query: Annotated[
        str,
        Field(
            description="Search text, e.g. 'midterm' or 'lab report'.",
            min_length=1,
        ),
    ],
    content_types: Annotated[
        Optional[List[str]],
        Field(
            description=(
                "Optional subset of content types to search. Defaults to all: "
                + ", ".join(SEARCH_CONTENT_TYPES)
            ),
        ),
    ] = None,
    limit: Annotated[
        int,
        Field(
            description="Maximum number of ranked results to return.",
            ge=1,
            le=50,
        ),
    ] = 10,
) -> SearchResultsResponse:
    """
    Search across course content with local ranking.

    Queries Canvas list endpoints with search_term where supported, merges
    syllabus/announcement/discussion body text without per-page body fetches,
    and returns bounded snippets only.

    On failure returns a structured error object (see docs/errors.md).
    """
    try:
        documents = await collect_search_documents(course_id, query, content_types)
        ranked = rank_documents(query, documents)
        truncated = len(ranked) > limit

        results: List[SearchResult] = []
        for document, score in ranked[:limit]:
            combined_text = f"{document.title}\n{document.body}".strip()
            results.append(
                SearchResult(
                    content_type=document.content_type,
                    title=document.title,
                    snippet=make_snippet(combined_text, query) or None,
                    score=round(score, 2),
                    course_id=document.course_id,
                    resource_id=document.resource_id,
                    url=document.url,
                    source_type=document.content_type,
                    canvas_url=document.url,
                )
            )
        return list_result(results, truncated=truncated)

    except Exception as e:
        return as_tool_error(e, source="canvas_rest")


search_course_content_tool: Final[Tool] = Tool.from_function(
    name="search_course_content",
    description=(
        "Search a Canvas course across syllabus, pages, assignments, modules, "
        "announcements, files, quizzes, and discussions. Returns ranked "
        "snippets only (not full page bodies)."
    ),
    fn=search_course_content,
)
