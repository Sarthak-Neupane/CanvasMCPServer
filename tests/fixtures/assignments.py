"""Sample assignment REST/GraphQL payloads."""

ASSIGNMENTS_CONNECTION_GRAPHQL = {
    "course": {
        "assignmentsConnection": {
            "nodes": [
                {
                    "_id": "200001",
                    "name": "Homework 1",
                    "dueAt": "2025-09-15T23:59:00Z",
                    "pointsPossible": 10.0,
                    "state": "published",
                    "htmlUrl": "https://canvas.example.edu/courses/100001/assignments/200001",
                }
            ],
            "pageInfo": {"endCursor": "cursor1", "hasNextPage": False},
        }
    }
}

ASSIGNMENT_DETAIL_GRAPHQL = {
    "assignment": {
        "_id": "200001",
        "name": "Homework 1",
        "description": "<p>Complete the worksheet.</p>",
        "dueAt": "2025-09-15T23:59:00Z",
        "pointsPossible": 10.0,
        "state": "published",
        "htmlUrl": "https://canvas.example.edu/courses/100001/assignments/200001",
        "submissionTypes": ["online_upload"],
    }
}

UPCOMING_ASSIGNMENTS_REST = [
    {
        "id": 200001,
        "title": "Homework 1",
        "html_url": "https://canvas.example.edu/courses/100001/assignments/200001",
        "due_at": "2025-09-15T23:59:00Z",
        "course_id": 100001,
        "context_name": "Intro to Testing",
    }
]
