"""Sample todo REST payloads."""

TODO_ITEMS_REST = [
    {
        "type": "submitting",
        "context_type": "course",
        "course_id": 100001,
        "html_url": "https://canvas.example.edu/courses/100001/assignments/200001",
        "assignment": {
            "id": 200001,
            "name": "Homework 1",
            "due_at": "2025-09-15T23:59:00Z",
            "points_possible": 10.0,
            "html_url": "https://canvas.example.edu/courses/100001/assignments/200001",
            "course_id": 100001,
        },
    }
]
