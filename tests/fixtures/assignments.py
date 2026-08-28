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

ASSIGNMENT_DETAIL_EXTERNAL_TOOL_GRAPHQL = {
    "assignment": {
        "_id": "200003",
        "name": "WebAssign Homework 1",
        "description": "",
        "dueAt": "2025-09-20T23:59:00Z",
        "unlockAt": None,
        "lockAt": None,
        "pointsPossible": 20.0,
        "state": "published",
        "htmlUrl": "https://canvas.example.edu/courses/100001/assignments/200003",
        "gradingType": "points",
        "submissionTypes": ["external_tool"],
        "allowedAttempts": 1,
        "course": {"_id": "100001", "name": "Intro to Testing"},
        "external_tool": {
            "url": "https://webassign.net/canvas/launch",
            "new_tab": True,
        },
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

ASSIGNMENT_REST_WITH_EMBEDS = {
    "id": 200001,
    "name": "Homework 1",
    "description": """
<div>
  <p>Read the <a href="/courses/100001/pages/week-1">Week 1 page</a>.</p>
  <p>Download:
    <a href="/courses/100001/files/500001/download?wrap=1"
       data-api-endpoint="/api/v1/courses/100001/files/500001"
       class="instructure_file_link">worksheet.pdf</a>
  </p>
  <p>Also see <a href="https://example.edu/resource">external resource</a>.</p>
</div>
""",
}
