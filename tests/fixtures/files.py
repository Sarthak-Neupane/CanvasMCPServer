"""Sample file/folder REST payloads."""

COURSE_META_REST = {
    "id": 100001,
    "name": "Intro to Testing",
}

FILE_LIST_REST = [
    {
        "id": 500001,
        "folder_id": 600001,
        "display_name": "syllabus.pdf",
        "filename": "syllabus.pdf",
        "content-type": "application/pdf",
        "url": "https://canvas.example.edu/files/500001/download",
        "size": 1024,
        "created_at": "2025-08-01T12:00:00Z",
        "updated_at": "2025-08-01T12:00:00Z",
        "mime_class": "pdf",
        "locked": False,
        "hidden": False,
        "visibility_level": "inherit",
    }
]

FOLDER_LIST_REST = [
    {
        "id": 600001,
        "name": "course files",
        "parent_folder_id": None,
        "folders_url": "https://canvas.example.edu/api/v1/folders/600001/folders",
        "files_url": "https://canvas.example.edu/api/v1/folders/600001/files",
        "files_count": 1,
        "folders_count": 0,
        "hidden": False,
        "locked": False,
    }
]

FILE_DETAIL_REST = {
    "id": 500001,
    "folder_id": 600001,
    "display_name": "syllabus.pdf",
    "filename": "syllabus.pdf",
    "content-type": "application/pdf",
    "url": "https://canvas.example.edu/files/500001/download",
    "size": 1024,
    "created_at": "2025-08-01T12:00:00Z",
    "updated_at": "2025-08-01T12:00:00Z",
    "mime_class": "pdf",
    "locked": False,
    "hidden": False,
    "locked_for_user": False,
    "hidden_for_user": False,
    "visibility_level": "inherit",
    "thumbnail_url": None,
    "preview_url": None,
}

ASSIGNMENT_WITH_FILE_EMBED_REST = {
    "id": 200001,
    "name": "Homework 1",
    "description": (
        '<p>Download the worksheet: '
        '<a href="/courses/100001/files/500001/download?wrap=1">worksheet.pdf</a></p>'
    ),
}

FILE_BYTES = b"%PDF-1.4 fake test content"
