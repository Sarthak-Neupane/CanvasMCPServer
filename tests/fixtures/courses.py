"""Sample course REST/GraphQL payloads."""

ALL_COURSES_GRAPHQL = {
    "allCourses": [
        {
            "id": "course-gid-100001",
            "name": "Intro to Testing",
            "courseCode": "TEST101",
            "term": {
                "id": "term-gid-9001",
                "_id": "9001",
                "name": "Fall 2025",
                "startAt": "2025-08-15T00:00:00Z",
                "endAt": "2025-12-15T23:59:59Z",
            },
        },
        {
            "id": "course-gid-100002",
            "name": "Advanced Testing",
            "courseCode": "TEST201",
            "term": {
                "id": "term-gid-9002",
                "_id": "9002",
                "name": "Spring 2026",
                "startAt": "2026-01-10T00:00:00Z",
                "endAt": "2026-05-10T23:59:59Z",
            },
        },
    ]
}

COURSE_BY_ID_GRAPHQL = {
    "course": {
        "_id": "100001",
        "id": "course-gid-100001",
        "name": "Intro to Testing",
        "courseCode": "TEST101",
        "state": "available",
    }
}

DASHBOARD_CARDS_REST = [
    {"id": 100001, "course_code": "TEST101", "original_name": "Intro to Testing"},
]

REST_COURSES_ACTIVE = [
    {
        "id": 100001,
        "name": "Intro to Testing",
        "course_code": "TEST101",
        "access_restricted_by_date": False,
        "term": {
            "id": 9001,
            "name": "Fall 2025",
            "start_at": "2025-08-15T00:00:00Z",
            "end_at": "2025-12-15T23:59:59Z",
        },
    },
    {
        "id": 100099,
        "name": "Old Dashboard-Excluded Course",
        "course_code": "OLD999",
        "access_restricted_by_date": False,
        "term": {"id": 9001, "name": "Fall 2025"},
    },
]

SYLLABUS_HTML_REST = {
    "id": 100001,
    "name": "Intro to Testing",
    "syllabus_body": (
        "<p>Welcome to Intro to Testing. Grading weights: Exams 50%, "
        "Homework 30%, Participation 20%.</p>"
    ),
}

SYLLABUS_FILE_LINK_REST = {
    "id": 100001,
    "name": "Intro to Testing",
    "syllabus_body": (
        '<p><a href="/courses/100001/files/500001/download" '
        'data-api-endpoint="https://canvas.example.edu/api/v1/courses/100001/files/500001">'
        "Download Syllabus.txt</a></p>"
    ),
}

SYLLABUS_EXTERNAL_LINK_REST = {
    "id": 100001,
    "name": "Intro to Testing",
    "syllabus_body": (
        '<p><a href="https://docs.google.com/document/d/12345/view">'
        "Course Syllabus Google Doc</a></p>"
    ),
}

SYLLABUS_FILE_REST = {
    "id": 500001,
    "folder_id": 600001,
    "display_name": "Syllabus.txt",
    "filename": "Syllabus.txt",
    "content-type": "text/plain",
    "url": "https://canvas.example.edu/files/500001/download?download_frd=1",
    "size": 128,
}

SYLLABUS_EMPTY_REST = {
    "id": 100001,
    "name": "Intro to Testing",
    "syllabus_body": None,
}
