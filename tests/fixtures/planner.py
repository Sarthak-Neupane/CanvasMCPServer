"""Sample planner REST payloads."""

PLANNER_ITEMS_REST = [
    {
        "context_type": "Course",
        "course_id": 100001,
        "planner_override": {
            "marked_complete": False,
            "dismissed": False,
        },
        "submissions": {
            "excused": False,
            "graded": False,
            "late": False,
            "missing": True,
            "needs_grading": False,
            "with_feedback": False,
        },
        "plannable_id": "200001",
        "plannable_type": "assignment",
        "plannable": {
            "id": 200001,
            "title": "Homework 1",
            "due_at": "2025-09-15T23:59:00Z",
        },
        "html_url": "/courses/100001/assignments/200001",
    },
    {
        "context_type": "Course",
        "course_id": 100001,
        "planner_override": None,
        "submissions": False,
        "plannable_id": "300001",
        "plannable_type": "planner_note",
        "plannable": {
            "id": 300001,
            "title": "Bring textbook",
            "todo_date": "2025-09-10T12:00:00Z",
        },
        "html_url": "/api/v1/planner_notes/300001",
    },
    {
        "context_type": "Course",
        "course_id": 100001,
        "planner_override": None,
        "submissions": False,
        "plannable_id": "400001",
        "plannable_type": "discussion_topic",
        "plannable": {
            "id": 400001,
            "title": "Week 1 discussion",
            "due_at": "2025-09-12T23:59:00Z",
        },
        "html_url": "/courses/100001/discussion_topics/400001",
    },
]
