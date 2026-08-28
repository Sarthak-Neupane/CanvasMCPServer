# Output conventions (P6.6)

This document defines how Canvas MCP tools shape successful responses so agents
can rely on consistent field naming, types, and list metadata.

## Naming: REST vs GraphQL tool families

| API source | Public field naming | Examples |
| --- | --- | --- |
| **GraphQL tools** | camelCase (matches Canvas GraphQL) | `courseCode`, `dueAt`, `pointsPossible`, `submissionStatus` |
| **REST tools** | snake_case (matches Canvas REST JSON) | `display_name`, `due_at`, `html_url`, `workflow_state` |

Do not mix conventions within a single model. GraphQL `_id` values are exposed
as `id` (string). REST numeric primary keys are usually `int` fields named
`id`, `page_id`, `quiz_id`, `discussion_id`, etc.

### Agent guidance

Treat all identifiers as opaque strings when comparing or passing between
tools, even when the JSON type is a number (`str(course_id)` is safe).

## Timestamps and scheduling policy

- **Timezone-aware ISO-8601**: Model timestamp fields (`due_at`, `dueAt`, `start_at`, `end_at`, `unlock_at`, `lock_at`, `posted_at`, `created_at`, `updated_at`) preserve Canvas timezone offsets without naive truncation.
- **Calendar-local date semantics**: When Canvas provides an all-day flag or date (`all_day: true`, `all_day_date: "yyyy-mm-dd"`), `all_day_date` is preserved as a `yyyy-mm-dd` string. For day-level natural language queries (e.g. "What's happening Friday?", "What is due today?"), agents should inspect `all_day_date` directly to prevent late-night local deadlines (e.g. 11:59 PM local) from skewing across midnight into the wrong day.
- **Planner vs Calendar semantics**:
  - `get_calendar_events`: Authoritative for day-specific scheduled events, timetable slots, and assignment deadlines on the calendar across enrolled courses.
  - `get_planner_items`: Structured academic planning feed including assignments, quizzes, discussions, pages, and personal planner notes with submission tracking flags (`missing`, `late`, `needs_grading`). Does not replace full calendar feeds.

## Nullable fields

Optional Canvas fields are `Optional[...]` in models and serialize as JSON
`null` when absent. An omitted key and `null` both mean “not provided by
Canvas for this resource.”

## List responses (`ListResult`)

Tools that return collections use `ListResult` instead of a bare JSON array:

```json
{
  "results": [ /* item models */ ],
  "result_count": 2,
  "truncated": false
}
```

| Field | Meaning |
| --- | --- |
| `results` | The items returned for this call |
| `result_count` | `len(results)` — explicit for agents that do not infer length |
| `truncated` | `true` when pagination caps or an explicit `limit` may have omitted additional Canvas items |

`truncated` is set when:

- REST/GraphQL pagination stops at `max_pages` while more pages exist
- `search_course_content` ranks more matches than the `limit` parameter
- `max_items` cuts a paginated fetch short

### `limit` parameter

List tools accept `limit` (default **50**, max **100**). Pagination stops early
when the cap is reached; `truncated` is set when Canvas may have more items.

Discovery list tools return **summaries only** (no HTML bodies). Use detail
tools (`get_page`, `get_assignment_details`, `get_discussion`, etc.) for full
content. `get_announcements` returns metadata only — use `get_discussion` for
the announcement message.

### Empty-State Semantics & Status Vocabulary

When Canvas resources or collections return empty or unavailable results, tools differentiate between true empty collections, missing features, external content, and permission boundaries.

### Shared Status Vocabulary

| Status | Meaning | Typical HTTP / GraphQL Source |
| --- | --- | --- |
| `ok` | Request completed successfully with matching items. | 200 OK / non-empty connection |
| `empty` | Request completed successfully but found zero matching items in Canvas. | 200 OK / empty array / no matches |
| `not_found` | Target course, assignment, page, quiz, or file does not exist. | 404 Not Found / null object |
| `not_applicable` | The requested sub-resource is not applicable (e.g. assignment has no rubric attached). | 200 OK with no rubric definition (`rubric_not_found`, details `reason: no_rubric`) |
| `permission_denied` | Canvas role permissions prevent listing the requested resource. | 401 Unauthorized / 403 Forbidden |
| `locked` | Resource is locked due to prerequisite, lock date, or progression requirement. | `locked: true`, `workflow_state: locked` |
| `not_yet_available` | Resource is scheduled for future access (`unlock_at` in the future). | `unlock_at > now` |
| `external_tool` | Assignment content or resources are hosted by a third-party LTI tool (e.g. WebAssign, MindTap, Zybooks). | `submission_types: ["external_tool"]` |
| `unsupported_by_canvas` | Classic Quizzes or other subsystem not enabled for this institution/course. | 404 on quiz listing returned as empty ListResult |
| `partial` | Batch or multi-resource download partially succeeded with some failures. | `completed_with_failures` on `DownloadBatchResult` |

### Empty-State Tool Audit Matrix

| Tool | Empty Results Meaning | Handling & Semantics |
| --- | --- | --- |
| `get_all_courses` | No active enrollments found | `ListResult(results=[], result_count=0, truncated=false)` |
| `get_assignments_for_course` | No assignments exist in course | `ListResult(results=[], result_count=0, truncated=false)` |
| `get_todo_items` | No pending student todo items | `ListResult(results=[], result_count=0, truncated=false)` |
| `get_planner_items` | No planner items in specified date window | `ListResult(results=[], result_count=0, truncated=false)` |
| `get_calendar_events` | No calendar events/deadlines in specified window | `ListResult(results=[], result_count=0, truncated=false)` |
| `get_course_modules` | No published modules in course | `ListResult(results=[], result_count=0, truncated=false)` |
| `get_module_items` | Empty module or no items match search filter | `ListResult(results=[], result_count=0, truncated=false)` |
| `get_course_files` | No files in course root or user lacks permission | `ListResult(results=[], result_count=0, truncated=false)` (or 403 error on restricted folders) |
| `get_course_pages` | No published wiki pages | `ListResult(results=[], result_count=0, truncated=false)` |
| `get_announcements` | No announcements in course | `ListResult(results=[], result_count=0, truncated=false)` |
| `get_course_discussions` | No discussion topics in course | `ListResult(results=[], result_count=0, truncated=false)` (announcements filtered out) |
| `get_course_quizzes` | No quizzes or classic quizzes disabled (404) | `ListResult(results=[], result_count=0, truncated=false)` |
| `get_assignment_rubric` | Assignment has no rubric attached | `tool_error(ErrorCode.RUBRIC_NOT_FOUND, "This assignment has no rubric.", details={"reason": "no_rubric", "status": "not_applicable"})` |
| `get_submission_status` | Assignment not submitted yet | `AssignmentSubmissions(submissions=[...])` with `submissionStatus='unsubmitted'` or empty list |
| `get_submission_feedback` | No comments or rubric grading | `SubmissionFeedback(comments=[], rubric_assessment={}, attachments=[])` |
| `get_assignment_resources` | No embedded files/links in description | `AssignmentResources(status='empty' | 'external_tool', empty_reason=..., resources=[])` |
| `get_page_resources` | No embedded files/links in page body | `PageResources(status='empty', empty_reason=..., resources=[])` |
| `download_*` (batch) | No matching files found or all skipped | `DownloadBatchResult(status='nothing_found' | 'all_skipped' | 'completed' | 'completed_with_failures' | 'failed')` |

## Wrapper models with embedded lists

Some tools return a single object with a named list plus `result_count`:

| Tool | Wrapper | Counted field |
| --- | --- | --- |
| `get_discussion_entries` | `DiscussionEntries` | `entries` |
| `get_assignment_resources` | `AssignmentResources` | `resources` |
| `get_page_resources` | `PageResources` | `resources` |
| `get_submission_status` | `AssignmentSubmissions` | `submissions` |
| `get_course_grades` | `CourseGrades` | `enrollments` |
| `get_assignment_rubric` | `Rubric` | `criteria` |
| `download_*` (batch) | `DownloadBatchResult` | `status`, `matched_count`, `downloaded_count`, `skipped_count`, `failed_count`, `result_count`, `downloaded`, `skipped`, `failed` |

## Implementation

- `ListResult`: `src/canvas_mcp_server/models/common/list_result_model.py`
- Builder: `list_result()` in `src/canvas_mcp_server/utils/list_results.py`
- Pagination metadata: `PaginatedResult` in `src/canvas_mcp_server/utils/pagination_types.py`
