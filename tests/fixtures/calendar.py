"""Sample calendar REST payloads."""

from tests.fixtures.courses import DASHBOARD_CARDS_REST

CALENDAR_EVENTS_REST = [
    {
        "id": 900001,
        "title": "Office hours",
        "start_at": "2025-09-10T14:00:00Z",
        "end_at": "2025-09-10T15:00:00Z",
        "all_day": False,
        "context_code": "course_100001",
        "context_name": "Intro to Testing",
        "html_url": "https://canvas.example.edu/calendar?event_id=900001",
        "location_name": "Room 101",
        "workflow_state": "active",
    }
]

CALENDAR_ASSIGNMENTS_REST = [
    {
        "id": "assignment_200001",
        "title": "Homework 1",
        "start_at": "2025-09-15T23:59:00Z",
        "end_at": "2025-09-15T23:59:00Z",
        "all_day": True,
        "all_day_date": "2025-09-15",
        "context_code": "course_100001",
        "context_name": "Intro to Testing",
        "html_url": "https://canvas.example.edu/courses/100001/assignments/200001",
        "workflow_state": "published",
    }
]

__all__ = [
    "DASHBOARD_CARDS_REST",
    "CALENDAR_EVENTS_REST",
    "CALENDAR_ASSIGNMENTS_REST",
]
