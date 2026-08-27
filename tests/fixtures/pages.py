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
