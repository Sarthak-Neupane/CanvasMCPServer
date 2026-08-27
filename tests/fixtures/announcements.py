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
            ]
        }
    }
}
