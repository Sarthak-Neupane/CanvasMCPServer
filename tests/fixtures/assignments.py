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

ASSIGNMENTS_CONNECTION_PAGE_1 = {
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
            "pageInfo": {"endCursor": "cursor1", "hasNextPage": True},
        }
    }
}

ASSIGNMENTS_CONNECTION_PAGE_2 = {
    "course": {
        "assignmentsConnection": {
            "nodes": [
                {
                    "_id": "200002",
                    "name": "Homework 2",
                    "dueAt": "2025-09-22T23:59:00Z",
                    "pointsPossible": 15.0,
                    "state": "published",
                    "htmlUrl": "https://canvas.example.edu/courses/100001/assignments/200002",
                }
            ],
            "pageInfo": {"endCursor": "cursor2", "hasNextPage": False},
        }
    }
}

ASSIGNMENT_DETAIL_GRAPHQL = {
    "assignment": {
        "_id": "200001",
        "name": "Homework 1",
        "description": "<p>Complete the worksheet.</p>",
        "dueAt": "2025-09-15T23:59:00Z",
        "unlockAt": "2025-09-01T00:00:00Z",
        "lockAt": None,
        "pointsPossible": 10.0,
        "state": "published",
        "htmlUrl": "https://canvas.example.edu/courses/100001/assignments/200001",
        "gradingType": "points",
        "submissionTypes": ["online_upload"],
        "allowedAttempts": 3,
        "course": {"_id": "100001", "name": "Intro to Testing"},
    }
}

UPCOMING_EVENTS_REST = [
    {
        "id": 900001,
        "title": "Study group",
        "context_code": "course_100001",
    },
    {
        "id": 900002,
        "context_code": "course_100001",
        "assignment": {
            "id": 200001,
            "name": "Homework 1",
            "due_at": "2025-09-15T23:59:00Z",
            "points_possible": 10.0,
            "course_id": 100001,
            "html_url": "https://canvas.example.edu/courses/100001/assignments/200001",
        },
    },
]
