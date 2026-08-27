"""Sample Canvas discussion REST payloads."""

DISCUSSIONS_LIST_REST = [
    {
        "id": 400001,
        "title": "Week 1 discussion",
        "posted_at": "2025-08-20T12:00:00Z",
        "last_reply_at": "2025-08-25T15:30:00Z",
        "require_initial_post": True,
        "user_can_see_posts": False,
        "discussion_subentry_count": 3,
        "read_state": "unread",
        "unread_count": 2,
        "published": True,
        "locked": False,
        "locked_for_user": False,
        "discussion_type": "threaded",
        "html_url": "https://canvas.example.edu/courses/100001/discussion_topics/400001",
    },
    {
        "id": 400002,
        "title": "Lab Q&A",
        "posted_at": "2025-08-22T09:00:00Z",
        "last_reply_at": None,
        "require_initial_post": False,
        "user_can_see_posts": True,
        "discussion_subentry_count": 0,
        "read_state": "read",
        "unread_count": 0,
        "published": True,
        "locked": True,
        "locked_for_user": True,
        "lock_explanation": "This discussion is locked until September 1.",
        "discussion_type": "side_comment",
        "html_url": "https://canvas.example.edu/courses/100001/discussion_topics/400002",
    },
]

DISCUSSION_DETAIL_REST = {
    "id": 400001,
    "title": "Week 1 discussion",
    "message": "<p>Introduce yourself.</p>",
    "posted_at": "2025-08-20T12:00:00Z",
    "require_initial_post": True,
    "user_can_see_posts": False,
    "discussion_subentry_count": 3,
    "published": True,
    "locked_for_user": False,
    "discussion_type": "threaded",
    "user_name": "Instructor Example",
    "html_url": "https://canvas.example.edu/courses/100001/discussion_topics/400001",
}

DISCUSSION_VIEW_REST = {
    "participants": [
        {
            "id": 10,
            "display_name": "Student One",
            "avatar_image_url": "https://canvas.example.edu/images/avatar.png",
        },
        {
            "id": 11,
            "display_name": "Student Two",
            "avatar_image_url": "https://canvas.example.edu/images/avatar.png",
        },
    ],
    "unread_entries": [12],
    "view": [
        {
            "id": 11,
            "user_id": 10,
            "parent_id": None,
            "message": "<p>Hello everyone!</p>",
            "replies": [
                {
                    "id": 12,
                    "user_id": 11,
                    "parent_id": 11,
                    "message": "<p>Welcome!</p>",
                    "replies": [],
                }
            ],
        }
    ],
}
