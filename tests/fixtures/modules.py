"""Sample module REST payloads."""

MODULES_LIST_REST = [
    {
        "id": 300001,
        "name": "Week 1",
        "position": 1,
        "unlock_at": None,
        "require_sequential_progress": False,
        "requirement_type": "all",
        "prerequisite_module_ids": [],
        "items_count": 3,
        "workflow_state": "active",
        "state": "started",
        "completed_at": None,
        "published": True,
    },
    {
        "id": 300002,
        "name": "Week 2",
        "position": 2,
        "unlock_at": "2025-09-01T00:00:00Z",
        "require_sequential_progress": True,
        "requirement_type": "all",
        "prerequisite_module_ids": [300001],
        "items_count": 2,
        "workflow_state": "active",
        "state": "locked",
        "completed_at": None,
        "published": True,
    },
]

MODULE_ITEMS_REST = [
    {
        "id": 400001,
        "module_id": 300001,
        "title": "Syllabus PDF",
        "type": "File",
        "content_id": 500001,
        "position": 1,
        "indent": 0,
        "url": "https://canvas.example.edu/api/v1/courses/100001/module_item_redirect/400001",
    },
    {
        "id": 400002,
        "module_id": 300001,
        "title": "Read Chapter 1",
        "type": "Page",
        "page_url": "chapter-1",
        "position": 2,
        "indent": 0,
        "url": "https://canvas.example.edu/api/v1/courses/100001/module_item_redirect/400002",
    },
]

MODULE_ITEM_DETAIL_REST = {
    "id": 400001,
    "module_id": 300001,
    "title": "Homework 1",
    "type": "Assignment",
    "content_id": 200001,
    "position": 1,
    "indent": 0,
    "completion_requirement": {
        "type": "must_submit",
        "completed": False,
    },
    "content_details": {
        "points_possible": 10.0,
        "due_at": "2025-09-15T23:59:00Z",
        "unlock_at": "2025-09-01T00:00:00Z",
        "lock_at": None,
        "locked_for_user": False,
        "lock_explanation": None,
    },
}
