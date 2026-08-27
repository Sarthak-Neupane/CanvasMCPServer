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

COURSE_GRADES_ROSTER_LEAK_GRAPHQL = {
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
                },
                {
                    "_id": "800002",
                    "type": "StudentEnrollment",
                    "user": {"_id": "700002", "name": "Classmate One"},
                    "grades": {
                        "currentScore": None,
                        "currentGrade": None,
                        "finalScore": None,
                        "finalGrade": None,
                    },
                },
            ]
        },
    }
}

COURSE_GRADES_TEACHER_SCOPED_GRAPHQL = {
    "course": {
        "_id": "100001",
        "name": "Intro to Testing",
        "permissions": {
            "viewAllGrades": True,
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

COURSE_GRADES_ALL_STUDENTS_GRAPHQL = {
    "course": {
        "_id": "100001",
        "name": "Intro to Testing",
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
                },
                {
                    "_id": "800002",
                    "type": "StudentEnrollment",
                    "user": {"_id": "700002", "name": "Classmate One"},
                    "grades": {
                        "currentScore": 88.0,
                        "currentGrade": "B+",
                        "finalScore": None,
                        "finalGrade": None,
                    },
                },
            ],
            "pageInfo": {"endCursor": "cursor1", "hasNextPage": False},
        },
    }
}
