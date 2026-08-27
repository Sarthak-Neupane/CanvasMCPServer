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

SUBMISSION_STATUS_ROSTER_LEAK_GRAPHQL = {
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
                    "user": {"_id": "700001", "name": "Test Student"},
                },
                {
                    "_id": "900002",
                    "state": "submitted",
                    "submissionStatus": "submitted",
                    "gradingStatus": "graded",
                    "score": 8.0,
                    "grade": "8",
                    "user": {"_id": "700002", "name": "Classmate"},
                },
            ]
        },
    }
}

SUBMISSION_FEEDBACK_REST = {
    "assignment_id": 200001,
    "user_id": 700001,
    "grade": "9",
    "score": 9.0,
    "workflow_state": "graded",
    "submitted_at": "2025-09-10T18:00:00Z",
    "graded_at": "2025-09-12T10:00:00Z",
    "submission_comments": [
        {
            "id": 101,
            "author_id": 800001,
            "author_name": "Dr. Instructor",
            "comment": "Nice work on the thesis.",
            "created_at": "2025-09-12T10:00:00Z",
            "attachment": {
                "id": 500010,
                "filename": "feedback.pdf",
                "display_name": "feedback.pdf",
                "content-type": "application/pdf",
                "url": "https://canvas.example.edu/files/500010/download",
            },
        }
    ],
    "rubric_assessment": {
        "crit1": {
            "points": 4.0,
            "rating_id": "rat1",
            "comments": "Clear thesis",
        }
    },
    "attachments": [
        {
            "id": 500001,
            "filename": "essay.pdf",
            "display_name": "essay.pdf",
            "content-type": "application/pdf",
            "url": "https://canvas.example.edu/files/500001/download",
        }
    ],
}
