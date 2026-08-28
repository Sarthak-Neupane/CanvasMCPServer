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

### Wrapper models with embedded lists

Some tools return a single object with a named list plus `result_count`:

| Tool | Wrapper | Counted field |
| --- | --- | --- |
| `get_discussion_entries` | `DiscussionEntries` | `entries` |
| `get_assignment_resources` | `AssignmentResources` | `resources` |
| `get_submission_status` | `AssignmentSubmissions` | `submissions` |
| `get_course_grades` | `CourseGrades` | `enrollments` |
| `get_assignment_rubric` | `Rubric` | `criteria` |
| `download_*` (batch) | `DownloadBatchResult` | `status`, `matched_count`, `downloaded_count`, `skipped_count`, `failed_count`, `result_count`, `downloaded`, `skipped`, `failed` |

## Implementation

- `ListResult`: `src/canvas_mcp_server/models/common/list_result_model.py`
- Builder: `list_result()` in `src/canvas_mcp_server/utils/list_results.py`
- Pagination metadata: `PaginatedResult` in `src/canvas_mcp_server/utils/pagination_types.py`
