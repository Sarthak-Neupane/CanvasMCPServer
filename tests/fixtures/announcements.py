"""Sample announcement GraphQL payloads."""

ANNOUNCEMENTS_GRAPHQL = {
    "course": {
        "discussionsConnection": {
            "nodes": [
                {
                    "_id": "110001",
                    "title": "Exam moved to Friday",
                    "message": "<p>The midterm is now on Friday.</p>",
                    "postedAt": "2025-09-01T14:00:00Z",
                    "contextName": "Intro to Testing",
                    "author": {"name": "Dr. Instructor"},
                }
            ],
            "pageInfo": {"endCursor": "cursor1", "hasNextPage": False},
        }
    }
}

ANNOUNCEMENTS_PAGE_1 = {
    "course": {
        "discussionsConnection": {
            "nodes": [
                {
                    "_id": "110001",
                    "title": "Exam moved to Friday",
                    "message": "<p>The midterm is now on Friday.</p>",
                    "postedAt": "2025-09-01T14:00:00Z",
                    "contextName": "Intro to Testing",
                    "author": {"name": "Dr. Instructor"},
                }
            ],
            "pageInfo": {"endCursor": "cursor1", "hasNextPage": True},
        }
    }
}

ANNOUNCEMENTS_PAGE_2 = {
    "course": {
        "discussionsConnection": {
            "nodes": [
                {
                    "_id": "110002",
                    "title": "Office hours update",
                    "message": "<p>Office hours moved to Tuesday.</p>",
                    "postedAt": "2025-09-02T14:00:00Z",
                    "contextName": "Intro to Testing",
                    "author": {"name": "Dr. Instructor"},
                }
            ],
            "pageInfo": {"endCursor": "cursor2", "hasNextPage": False},
        }
    }
}
