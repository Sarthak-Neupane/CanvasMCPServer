"""Sample payloads for course content search tests."""

SYLLABUS_SEARCH_REST = {
    "id": 100001,
    "name": "Intro to Testing",
    "syllabus_body": "<p>The midterm exam covers chapters 1-4.</p>",
}

PAGES_SEARCH_REST = [
    {
        "page_id": 700001,
        "url": "midterm-review",
        "title": "Midterm review guide",
        "updated_at": "2025-09-01T12:00:00Z",
    }
]

ASSIGNMENTS_SEARCH_GRAPHQL = {
    "course": {
        "assignmentsConnection": {
            "nodes": [
                {
                    "_id": "200001",
                    "name": "Midterm essay",
                    "htmlUrl": "https://canvas.example.edu/courses/100001/assignments/200001",
                    "dueAt": "2025-10-01T23:59:00Z",
                }
            ]
        }
    }
}
