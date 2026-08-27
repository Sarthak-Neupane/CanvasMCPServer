"""Sample grades GraphQL / user REST payloads."""

USERS_SELF_REST = {
    "id": 700001,
    "name": "Test Student",
    "short_name": "Test S.",
    "login_id": "teststudent",
}

COURSE_GRADES_GRAPHQL = {
    "course": {
        "_id": "100001",
        "name": "Intro to Testing",
        "permissions": {
            "viewAllGrades": False,
            "manageGrades": False,
        },
        "enrollmentsConnection": {
            "nodes": [
                {
                    "_id": "800001",
                    "type": "StudentEnrollment",
                    "user": {"_id": "700001", "name": "Test Student"},
                    "grades": {
                        "currentScore": 92.5,
                        "currentGrade": "A-",
                        "finalScore": None,
                        "finalGrade": None,
                    },
                }
            ]
        },
    }
}
