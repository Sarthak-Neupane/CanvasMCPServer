# MCP tool reference (student read-only v1)

All **34** tools are read-only except the four `download_*` tools, which write
files to `CANVAS_DOWNLOAD_DIR` only. On failure, tools return a structured error
object — see [errors.md](errors.md).

**List tools** return `ListResult` (`results`, `result_count`, `truncated`) with
default `limit=50` (max 100). See [output-conventions.md](output-conventions.md).

| Tool | API | Kind | Writes disk | Notes |
| --- | --- | --- | --- | --- |
| `get_all_courses` | GraphQL + REST | list | no | `active_only`, `term`, `limit` |
| `get_course_by_id` | GraphQL | detail | no | Numeric or global course id |
| `get_course_syllabus` | REST | detail | no | Syllabus HTML + plain text |
| `get_course_pages` | REST | list | no | Metadata only; `search_term`, `limit` |
| `get_page` | REST | detail | no | Slug, id, or Canvas path |
| `get_course_modules` | REST | list | no | Structure only; `search_term`, `limit` |
| `get_module_items` | REST | list | no | No `content_details`; `search_term`, `limit` |
| `get_module_item_details` | REST | detail | no | Lock/due/points when available |
| `get_course_files` | REST | list | no | `search_term`, `content_type`, `limit` |
| `get_course_folders` | REST | list | no | Flat folder list; `limit` |
| `get_folder_files` | REST | list | no | Files in one folder; `limit` |
| `get_file_details` | REST | detail | no | Metadata + download URL |
| `get_assignments_for_course` | GraphQL | list | no | Summaries only; `limit` |
| `get_assignment_details` | GraphQL | detail | no | Description HTML + text |
| `get_assignment_resources` | REST | wrapper | no | Linked files/pages/URLs in description |
| `get_upcoming_assignments` | REST | list | no | Cross-course; `limit` |
| `get_todo_items` | REST | list | no | Optional `course_id`; `limit` |
| `get_planner_items` | REST | list | no | `start_date`, `end_date`, `course_id`, `limit` |
| `get_calendar_events` | REST | list | no | Events + assignment due dates; `limit` |
| `get_course_discussions` | REST | list | no | Excludes announcements; `search_term`, `limit` |
| `get_discussion` | REST | detail | no | Prompt HTML + lock metadata |
| `get_discussion_entries` | REST | wrapper | no | Threaded replies; may return `discussion_locked` |
| `get_course_quizzes` | REST | list | no | No questions; `search_term`, `limit` |
| `get_quiz` | REST | detail | no | Instructions/settings; no questions |
| `get_announcements` | GraphQL | list | no | Metadata only; use `get_discussion` for body |
| `get_course_grades` | GraphQL | wrapper | no | Self-only for students; teacher sees all |
| `get_submission_status` | GraphQL | wrapper | no | Self submissions only |
| `get_submission_feedback` | REST | detail | no | Comments, rubric, attachments; self only |
| `get_assignment_rubric` | REST | wrapper | no | Criteria template; no student scores |
| `search_course_content` | REST + GraphQL | list | no | Local ranking; `limit` default 10 |
| `download_file` | REST | action | **yes** | One file by id |
| `download_course_files` | REST | action | **yes** | Batch; same filters as `get_course_files` |
| `download_module_files` | REST | action | **yes** | File-type module items only |
| `download_assignment_files` | REST | action | **yes** | Embedded files in assignment HTML |

## Typical workflows

**Course overview:** `get_all_courses` → `get_course_by_id` / `get_course_syllabus`

**Weekly plan:** `get_planner_items` or `get_calendar_events` + `get_todo_items`

**Assignment deep-dive:** `get_assignments_for_course` → `get_assignment_details` →
`get_assignment_resources` → `get_submission_status` / `get_submission_feedback`

**Module navigation:** `get_course_modules` → `get_module_items` →
`get_module_item_details` / `get_page` / `get_assignment_details`

**Find content:** `search_course_content` with a keyword, then call the matching
detail tool for full text.
