"""Sample Canvas wiki page REST payloads."""

PAGES_LIST_REST = [
    {
        "page_id": 700001,
        "url": "week-1-overview",
        "title": "Week 1 Overview",
        "created_at": "2025-08-01T12:00:00Z",
        "updated_at": "2025-08-10T09:00:00Z",
        "published": True,
        "front_page": False,
        "locked_for_user": False,
    },
    {
        "page_id": 700002,
        "url": "syllabus-notes",
        "title": "Syllabus Notes",
        "created_at": "2025-08-02T12:00:00Z",
        "updated_at": "2025-08-11T09:00:00Z",
        "published": True,
        "front_page": True,
        "locked_for_user": False,
    },
]

PAGE_DETAIL_REST = {
    "page_id": 700001,
    "url": "week-1-overview",
    "title": "Week 1 Overview",
    "created_at": "2025-08-01T12:00:00Z",
    "updated_at": "2025-08-10T09:00:00Z",
    "published": True,
    "front_page": False,
    "locked_for_user": False,
    "body": "<h1>Week 1</h1><p>Read chapter 1.</p><script>bad()</script>",
}

PAGE_DETAIL_WITH_RESOURCES_REST = {
    "page_id": 700003,
    "url": "lecture-2-materials",
    "title": "Lecture 2 Materials",
    "created_at": "2025-08-03T12:00:00Z",
    "updated_at": "2025-08-12T09:00:00Z",
    "published": True,
    "front_page": False,
    "locked_for_user": False,
    "body": (
        '<p>Download the <a href="/courses/100001/files/500002/download" '
        'data-api-endpoint="https://canvas.example.edu/api/v1/courses/100001/files/500002">'
        "Lecture Slides</a> and review "
        '<a href="/courses/100001/pages/week-1-overview">Week 1 Overview</a>. '
        'Also see <a href="https://example.com/reading">External Reading</a>.</p>'
    ),
}

PAGE_DETAIL_EMPTY_RESOURCES_REST = {
    "page_id": 700004,
    "url": "announcements-summary",
    "title": "Announcements Summary",
    "created_at": "2025-08-04T12:00:00Z",
    "updated_at": "2025-08-13T09:00:00Z",
    "published": True,
    "front_page": False,
    "locked_for_user": False,
    "body": "<p>No extra links or resources here.</p>",
}
