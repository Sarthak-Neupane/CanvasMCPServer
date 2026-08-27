"""Sample submission GraphQL payloads."""

SUBMISSION_STATUS_GRAPHQL = {
    "assignment": {
        "_id": "200001",
        "name": "Homework 1",
        "dueAt": "2025-09-15T23:59:00Z",
        "pointsPossible": 10.0,
        "submissionsConnection": {
            "nodes": [
                {
                    "_id": "900001",
                    "state": "submitted",
                    "submissionStatus": "submitted",
                    "gradingStatus": "graded",
                    "score": 9.0,
                    "grade": "9",
                    "excused": False,
                    "late": False,
                    "missing": False,
                    "attempt": 1,
                    "submissionType": "online_upload",
                    "submittedAt": "2025-09-10T18:00:00Z",
                    "gradedAt": "2025-09-12T10:00:00Z",
                    "cachedDueDate": "2025-09-15T23:59:00Z",
                    "user": {"_id": "700001", "name": "Test Student"},
                }
            ]
        },
    }
}
