"""Collect searchable documents from Canvas course sources."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from ...utils import canvas_api_client, extract_graphql_data
from ...utils.graphql_pagination import paginate_graphql_connection
from ...utils.html import html_to_text
from ._types import SEARCH_CONTENT_TYPES, SearchDocument

ASSIGNMENTS_SEARCH_GRAPHQL = """
query ($courseId: ID!, $searchTerm: String!, $first: Int!, $after: String) {
  course(id: $courseId) {
    assignmentsConnection(
      first: $first
      after: $after
      filter: {searchTerm: $searchTerm}
    ) {
      nodes {
        _id
        name
        htmlUrl
        dueAt
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}
"""

ANNOUNCEMENTS_SEARCH_GRAPHQL = """
query ($courseId: ID!, $searchTerm: String!, $first: Int!, $after: String) {
  course(id: $courseId) {
    discussionsConnection(
      first: $first
      after: $after
      filter: {isAnnouncement: true, searchTerm: $searchTerm}
    ) {
      nodes {
        _id
        title
        message
        postedAt
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}
"""

PER_SOURCE_LIMIT = 50
COLLECTOR_CONCURRENCY = 6


def _course_page_url(course_id: str, page_slug: str) -> str:
    return f"/courses/{course_id}/pages/{page_slug}"


def _course_discussion_url(course_id: str, discussion_id: str) -> str:
    return f"/courses/{course_id}/discussion_topics/{discussion_id}"


async def _collect_syllabus(course_id: str) -> List[SearchDocument]:
    response = await canvas_api_client.get_rest(
        endpoint=f"v1/courses/{course_id}",
        params={"include[]": "syllabus_body"},
    )
    data = response.data
    if not isinstance(data, dict):
        return []

    body_html = data.get("syllabus_body") or ""
    title = str(data.get("name") or "Course syllabus")
    body = html_to_text(body_html) if body_html else ""
    if not body and not title:
        return []

    return [
        SearchDocument(
            content_type="syllabus",
            title=title,
            body=body,
            course_id=course_id,
            resource_id=str(course_id),
            url=f"/courses/{course_id}/assignments/syllabus",
        )
    ]


async def _collect_pages(course_id: str, query: str) -> List[SearchDocument]:
    paginated = await canvas_api_client.get_rest_paginated(
        endpoint=f"v1/courses/{course_id}/pages",
        params={"per_page": PER_SOURCE_LIMIT, "search_term": query},
        max_items=PER_SOURCE_LIMIT,
    )

    documents: List[SearchDocument] = []
    for page in paginated.items:
        if not isinstance(page, dict):
            continue
        slug = page.get("url")
        title = str(page.get("title") or slug or "Untitled page")
        page_id = page.get("page_id")
        documents.append(
            SearchDocument(
                content_type="page",
                title=title,
                body=title,
                course_id=course_id,
                resource_id=str(page_id or slug or ""),
                url=_course_page_url(course_id, str(slug)) if slug else None,
                updated_at=page.get("updated_at"),
            )
        )
    return documents


async def _collect_assignments(course_id: str, query: str) -> List[SearchDocument]:
    async def fetch_connection(after: str | None) -> Dict[str, Any]:
        response = await canvas_api_client.post_graphql_query(
            query=ASSIGNMENTS_SEARCH_GRAPHQL,
            variables={
                "courseId": course_id,
                "searchTerm": query,
                "first": PER_SOURCE_LIMIT,
                "after": after,
            },
        )
        data = extract_graphql_data(response)
        course = data.get("course")
        if not isinstance(course, dict):
            return {"nodes": []}
        return course.get("assignmentsConnection") or {"nodes": []}

    paginated = await paginate_graphql_connection(
        fetch_connection,
        max_pages=5,
        max_items=PER_SOURCE_LIMIT,
    )
    documents: List[SearchDocument] = []
    for node in paginated.items:
        if not isinstance(node, dict):
            continue
        assignment_id = node.get("_id")
        title = str(node.get("name") or "Untitled assignment")
        documents.append(
            SearchDocument(
                content_type="assignment",
                title=title,
                body=title,
                course_id=course_id,
                resource_id=str(assignment_id or ""),
                url=node.get("htmlUrl"),
                updated_at=node.get("dueAt"),
            )
        )
    return documents


async def _collect_modules(course_id: str, query: str) -> List[SearchDocument]:
    paginated = await canvas_api_client.get_rest_paginated(
        endpoint=f"v1/courses/{course_id}/modules",
        params={"per_page": PER_SOURCE_LIMIT, "search_term": query},
        max_items=PER_SOURCE_LIMIT,
    )

    documents: List[SearchDocument] = []
    for module in paginated.items:
        if not isinstance(module, dict):
            continue
        module_id = module.get("id")
        title = str(module.get("name") or "Untitled module")
        documents.append(
            SearchDocument(
                content_type="module",
                title=title,
                body=title,
                course_id=course_id,
                resource_id=str(module_id or ""),
                url=f"/courses/{course_id}/modules/{module_id}"
                if module_id is not None
                else None,
            )
        )
    return documents


async def _collect_announcements(course_id: str, query: str) -> List[SearchDocument]:
    async def fetch_connection(after: str | None) -> Dict[str, Any]:
        response = await canvas_api_client.post_graphql_query(
            query=ANNOUNCEMENTS_SEARCH_GRAPHQL,
            variables={
                "courseId": course_id,
                "searchTerm": query,
                "first": PER_SOURCE_LIMIT,
                "after": after,
            },
        )
        data = extract_graphql_data(response)
        course = data.get("course")
        if not isinstance(course, dict):
            return {"nodes": []}
        return course.get("discussionsConnection") or {"nodes": []}

    paginated = await paginate_graphql_connection(
        fetch_connection,
        max_pages=5,
        max_items=PER_SOURCE_LIMIT,
    )
    documents: List[SearchDocument] = []
    for node in paginated.items:
        if not isinstance(node, dict):
            continue
        announcement_id = node.get("_id")
        title = str(node.get("title") or "Announcement")
        message = node.get("message") or ""
        body = html_to_text(message) if message else title
        documents.append(
            SearchDocument(
                content_type="announcement",
                title=title,
                body=body,
                course_id=course_id,
                resource_id=str(announcement_id or ""),
                url=_course_discussion_url(course_id, str(announcement_id))
                if announcement_id
                else None,
                updated_at=node.get("postedAt"),
            )
        )
    return documents


async def _collect_files(course_id: str, query: str) -> List[SearchDocument]:
    paginated = await canvas_api_client.get_rest_paginated(
        endpoint=f"v1/courses/{course_id}/files",
        params={"per_page": PER_SOURCE_LIMIT, "search_term": query},
        max_items=PER_SOURCE_LIMIT,
    )

    documents: List[SearchDocument] = []
    for file_obj in paginated.items:
        if not isinstance(file_obj, dict):
            continue
        file_id = file_obj.get("id")
        title = str(
            file_obj.get("display_name")
            or file_obj.get("filename")
            or "Untitled file"
        )
        documents.append(
            SearchDocument(
                content_type="file",
                title=title,
                body=title,
                course_id=course_id,
                resource_id=str(file_id or ""),
                url=file_obj.get("url"),
                updated_at=file_obj.get("updated_at") or file_obj.get("modified_at"),
            )
        )
    return documents


async def _collect_quizzes(course_id: str, query: str) -> List[SearchDocument]:
    paginated = await canvas_api_client.get_rest_paginated(
        endpoint=f"v1/courses/{course_id}/quizzes",
        params={"per_page": PER_SOURCE_LIMIT, "search_term": query},
        max_items=PER_SOURCE_LIMIT,
    )

    documents: List[SearchDocument] = []
    for quiz in paginated.items:
        if not isinstance(quiz, dict):
            continue
        quiz_id = quiz.get("id")
        title = str(quiz.get("title") or "Untitled quiz")
        description = quiz.get("description") or ""
        body = html_to_text(description) if description else title
        documents.append(
            SearchDocument(
                content_type="quiz",
                title=title,
                body=body,
                course_id=course_id,
                resource_id=str(quiz_id or ""),
                url=quiz.get("html_url"),
                updated_at=quiz.get("due_at"),
            )
        )
    return documents


async def _collect_discussions(course_id: str, query: str) -> List[SearchDocument]:
    paginated = await canvas_api_client.get_rest_paginated(
        endpoint=f"v1/courses/{course_id}/discussion_topics",
        params={
            "per_page": PER_SOURCE_LIMIT,
            "search_term": query,
            "only_announcements": False,
        },
        max_items=PER_SOURCE_LIMIT,
    )

    documents: List[SearchDocument] = []
    for topic in paginated.items:
        if not isinstance(topic, dict):
            continue
        discussion_id = topic.get("id")
        title = str(topic.get("title") or "Untitled discussion")
        message = topic.get("message") or ""
        body = html_to_text(message) if message else title
        documents.append(
            SearchDocument(
                content_type="discussion",
                title=title,
                body=body,
                course_id=course_id,
                resource_id=str(discussion_id or ""),
                url=topic.get("html_url")
                or _course_discussion_url(course_id, str(discussion_id)),
                updated_at=topic.get("last_reply_at") or topic.get("posted_at"),
            )
        )
    return documents


_COLLECTORS = {
    "page": _collect_pages,
    "assignment": _collect_assignments,
    "module": _collect_modules,
    "announcement": _collect_announcements,
    "file": _collect_files,
    "quiz": _collect_quizzes,
    "discussion": _collect_discussions,
}


async def _collect_one(
    content_type: str,
    course_id: str,
    query: str,
    semaphore: asyncio.Semaphore,
) -> List[SearchDocument]:
    async with semaphore:
        try:
            if content_type == "syllabus":
                return await _collect_syllabus(course_id)
            collector = _COLLECTORS.get(content_type)
            if collector is None:
                return []
            return await collector(course_id, query)
        except Exception:
            return []


async def collect_search_documents(
    course_id: str,
    query: str,
    content_types: Optional[List[str]] = None,
) -> List[SearchDocument]:
    """Fetch searchable documents from all requested sources in parallel."""
    selected = content_types or list(SEARCH_CONTENT_TYPES)
    unknown = [value for value in selected if value not in SEARCH_CONTENT_TYPES]
    if unknown:
        raise ValueError(
            f"Unknown content_types: {', '.join(unknown)}. "
            f"Allowed: {', '.join(SEARCH_CONTENT_TYPES)}"
        )

    semaphore = asyncio.Semaphore(COLLECTOR_CONCURRENCY)
    results = await asyncio.gather(
        *[
            _collect_one(content_type, course_id, query, semaphore)
            for content_type in selected
        ]
    )
    documents: List[SearchDocument] = []
    for batch in results:
        documents.extend(batch)
    return documents
