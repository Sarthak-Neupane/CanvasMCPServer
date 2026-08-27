# Canvas API Knowledgebase

Curated reference for working on this MCP server, synthesized from the official
[Instructure Developer Documentation](https://developerdocs.instructure.com/get_started).
This project talks to Canvas via **GraphQL** (`POST {CANVAS_BASE_URL}/graphql`), so the
GraphQL sections are primary; REST sections are kept because the GraphQL API does not
cover everything and REST fallback may be needed.

---

## 1. GraphQL API (primary transport for this project)

Source: [GraphQL basics](https://developerdocs.instructure.com/services/canvas/basics/file.graphql)
and [GraphQL endpoint reference](https://developerdocs.instructure.com/services/canvas/resources/graph_ql).

### Endpoint

```
POST /api/graphql
```

There is a single endpoint for all queries and mutations. Request body parameters:

| Parameter       | Type   | Description                                                        |
| --------------- | ------ | ------------------------------------------------------------------ |
| `query`         | string | The GraphQL query or mutation to execute                           |
| `variables`     | Hash   | Values for variables referenced by the query                       |
| `operationName` | string | Which operation to run if the document defines more than one       |

Auth is a Bearer token header, same as REST:

```bash
curl https://<canvas>/api/graphql \
  -H 'Authorization: Bearer <ACCESS_TOKEN>' \
  -d query='query courseInfo($courseId: ID!) {
       course(id: $courseId) { id _id name }
     }' \
  -d variables[courseId]=1
```

Important for this repo: `CanvasAPIClient.post_graphql_query()` appends `graphql` to
`CANVAS_BASE_URL`, so the env var must end at `/api` (NOT `/api/v1`).

### `id` vs `_id` (Relay object identification)

- `id` returns a **global Relay identifier** (base64, e.g. `"Q291cnNlLTE="`).
- `_id` returns the **traditional numeric REST id** (e.g. `"1"`).
- Query both when you may need to cross-reference REST.

Fetch any object by global id via `node`:

```graphql
{ node(id: "Q291cnNlLTE=") { ... on Course { _id name term { name } } } }
```

Fetch by REST-style id via `legacyNode` (type must be specified):

```graphql
{ legacyNode(type: Course, _id: "1") { ... on Course { _id name } } }
```

Type-specific fields like `course(id:)` accept **either** id form:

```graphql
{
  c1: course(id: "1")            { _id name }
  c2: course(id: "Q291cnNlLTE=") { _id name }
}
```

### Pagination (Relay Connection Spec)

Collections use `*Connection` fields with cursor pagination. Request reasonable page
sizes to avoid being limited.

```graphql
{
  course(id: "1") {
    assignmentsConnection(first: 10, after: "XYZ") {  # after = endCursor of prev page
      nodes { id name }
      pageInfo { endCursor hasNextPage }
    }
  }
}
```

Some connections also support `pageInfo { totalCount }` (total ignoring pagination),
but only where explicitly configured — not all connection types have it.

### Schema exploration

- **GraphiQL** in-browser IDE: `https://<your-institution>.instructure.com/graphiql`
  (also works on test/beta domains; returns that environment's data). The Explorer
  sidebar lists all available queries/mutations; purple text = input arguments.
- Permissions mirror the REST API: users only see what their role allows (a student
  can't see another student's grades; an instructor can see their course's students).
- The GraphQL API is **incomplete** relative to REST — fields are added as needed.
  If something is missing in GraphQL, fall back to REST (`/api/v1/...`).
- Granting the GraphQL token scope (`url:POST|/api/graphql`) allows any query or
  mutation the authenticated user is otherwise permitted to perform.

---

## 2. Authentication

Source: [OAuth2 Overview](https://developerdocs.instructure.com/services/canvas/oauth2/file.oauth)
and [Developer Keys](https://developerdocs.instructure.com/services/canvas/oauth2/file.developer_keys).

### Manual access tokens (what this project currently uses)

- Generate from Canvas: profile menu → `/profile` → "Approved Integrations" →
  new access token. It is shown **once**; treat it like a password.
- Single-user/testing only. Applications used by multiple users MUST implement
  OAuth2 (asking other users to paste manual tokens violates Canvas API policy).
- Send as header (preferred over query string): `Authorization: Bearer <TOKEN>`.

### OAuth2 flow (needed if this server is ever distributed)

1. `GET /login/oauth2/auth?client_id=XXX&response_type=code&state=YYY&redirect_uri=...`
2. Canvas redirects back with `?code=XXX&state=YYY` (or `?error=access_denied`).
3. `POST /login/oauth2/token` with `grant_type=authorization_code`, `client_id`,
   `client_secret`, `redirect_uri`, `code` → access token + refresh token.
- Developer-key tokens issued after Oct 2015 **expire after 1 hour**; refresh with
  `grant_type=refresh_token` (same refresh token is reused; response has no new one).
- Client ID/secret come from a **Developer Key** issued by the institution admin
  (Canvas Cloud) or Site Admin account (open source Canvas).
- Logout / revoke: `DELETE /login/oauth2/token`.

### Error signals

- `401` with a `WWW-Authenticate` header ⇒ token invalid/expired (re-auth), or the
  token was issued on a **different Canvas domain** than the one being called.
- `401` without that header ⇒ plain permission problem.

---

## 3. Throttling / rate limits

Source: [Throttling](https://developerdocs.instructure.com/services/canvas/basics/file.throttling).

- Quota-based: every request has a cost; quota replenishes over time.
- Exceeding it returns **`429 Forbidden (Rate Limit Exceeded)`** — retry later.
- Response headers: `X-Request-Cost` (cost of this request) and
  `X-Rate-Limit-Remaining` (remaining quota, when throttling applies).
- This server retries **429**, **5xx**, and transient **network/timeout** errors
  with exponential backoff (`CANVAS_RETRY_BASE_DELAY`, default 1s) up to
  `CANVAS_MAX_RETRIES` (default 3). When Canvas sends **`Retry-After`**, the
  longer of backoff and that header is used. **400/401/403/404** are never retried.
- Serial clients (one request at a time) are unlikely to be throttled. Parallel
  requests incur a pre-flight penalty (credited back on completion).
- Each OAuth access token has its own quota.

---

## 4. REST API essentials (fallback)

### Base URL and pagination

- REST lives at `/api/v1/...` (GraphQL at `/api/graphql`) — do not mix them up.
- Source: [Pagination](https://developerdocs.instructure.com/services/canvas/basics/file.pagination).
  Lists default to **10 items**; use `?per_page=N` (server-capped). Follow the
  `Link` response header (`rel="current" | next | prev | first | last`) — treat the
  URLs as opaque; parse the header name case-insensitively. `rel="last"` may be
  omitted when the total count is expensive. If you authenticate via
  `access_token` query param, it is stripped from the returned links.
- **Server helper**: `canvas_api_client.get_rest_paginated(...)` returns a
  `PaginatedResult` (`items`, `truncated`) and aggregates list pages via
  `parse_link_header` in `utils/rest_pagination.py`. MCP list tools wrap
  `items` in `ListResult` (`results`, `result_count`, `truncated`) — see
  [output-conventions.md](output-conventions.md).
- **GraphQL connections**: `paginate_graphql_connection` in
  `utils/graphql_pagination.py` follows Relay `pageInfo.endCursor` /
  `hasNextPage` (default 50 per page, max 10 pages). Used by assignments,
  announcements, teacher grade rosters, submission status, and search
  GraphQL collectors. Single-object queries (`course`, `assignment` detail)
  and scoped student grade lookups do not paginate.
- **Not paginated** (single-object endpoints): file/assignment/page/discussion
  detail, syllabus body, submission feedback, rubric include, dashboard cards
  (bounded), discussion topic view.
- **HTTP client lifecycle**: `canvas_api_client.start()` opens one shared
  `httpx.AsyncClient` for API and download traffic when the MCP server boots;
  `canvas_api_client.aclose()` runs on SIGINT/SIGTERM shutdown. Tests and
  one-off scripts without `start()` fall back to per-request clients.

### Timestamps (tool output policy)

- Canvas REST and GraphQL return datetimes as ISO-8601 strings, usually with a
  `Z` UTC suffix or a numeric offset.
- Pydantic `datetime` fields on tool models parse those strings into
  **timezone-aware** `datetime` values automatically.
- Do not strip offsets or normalize to naive local time in tools — return what
  Canvas provides so clients can format in the user's locale.
- Optional date **filters** passed to tools (`start_date`, `end_date`) accept
  `yyyy-mm-dd` or full ISO-8601; they are forwarded to Canvas as given.

### Courses resource (most relevant to current tools)

Source: [Courses](https://developerdocs.instructure.com/services/canvas/resources/courses).

Key endpoints:

- `GET /api/v1/courses` — list your courses. Filters: `enrollment_type`
  (teacher|student|ta|observer|designer), `enrollment_state`
  (active|invited_or_pending|completed), `state[]`
  (unpublished|available|completed|deleted), `exclude_blueprint_courses`, and
  `include[]` (see below).
- `GET /api/v1/courses/:id` — single course (also `include[]`; a course with
  workflow state `deleted` returns "resource does not exist" error).
- `GET /api/v1/users/:user_id/courses` — courses for another user (observer/admin).
- `GET /api/v1/courses/:course_id/users/:user_id/progress` — CourseProgress.
- `GET /api/v1/courses/:course_id/users`, `/students`, `/search_users` — rosters.

`include[]` values (these are what `constants/course_query_includes.py` mirrors):
`needs_grading_count`, `syllabus_body`, `public_description`, `total_scores`,
`current_grading_period_scores`, `grading_periods`, `term`, `account`,
`course_progress`, `sections`, `storage_quota_used_mb`, `total_students`,
`passback_status`, `favorites`, `teachers`, `observed_users`, `tabs`,
`course_image`, `banner_image`, `concluded`, `post_manually`.

Core Course object fields (REST names are snake_case; GraphQL uses camelCase like
`courseCode`, `startAt`): `id`, `name`, `course_code`, `workflow_state`
(unpublished|available|completed|deleted), `account_id`, `enrollment_term_id`,
`created_at`, `start_at`, `end_at`, `locale`, `total_students`, `default_view`
(feed|wiki|modules|assignments|syllabus), `syllabus_body`, `term`,
`course_progress`, `permissions`, `is_public`, `storage_quota_mb`,
`hide_final_grades`, `course_format`, `time_zone`, `blueprint`, `template`.

Related objects (match this repo's Pydantic models):

- **Term**: `id`, `name`, `start_at`, `end_at` → `models/courses/course_term_model.py`
- **CourseProgress**: `requirement_count`, `requirement_completed_count`,
  `next_requirement_url` (null when done/non-sequential), `completed_at` (null if
  incomplete) → `course_progress_model.py`. Errors if course isn't module-based or
  user isn't a student.
- **CalendarLink**: `ics` URL → `course_calendar_model.py`

### Response conventions

- Success: 200/201 with JSON fields.
- Errors: 4xx with `{"errors": [{"message": "..."}]}` (e.g. "Invalid access token.").

---

## 5. GraphQL schema notes for tools (verified against canvas-lms source)

Verified from `app/graphql/` in the canvas-lms repository. Argument and field
names below are the GraphQL camelCase forms.

### Top-level Query fields

`allCourses`, `course(id:)`, `assignment(id:)`, `submission(id: | assignmentId: + userId:)`,
`user(id:)`, `term(id:)`, `node(id:)`, `legacyNode(type:, _id:)`. There is **no**
top-level query for todo items or upcoming events — those are REST-only.

### Assignments

- `course(id:) { assignmentsConnection(first:, after:, filter: { searchTerm, userId, gradingPeriodId, submissionTypes }) }`
- Assignment fields: `_id`, `name`, `description` (HTML), `dueAt`, `lockAt`,
  `unlockAt`, `pointsPossible`, `state` (unpublished|published|deleted),
  `htmlUrl`, `gradingType`, `submissionTypes`, `allowedAttempts`, `quiz`,
  `rubric`, `course { _id name }`, `hasSubmittedSubmissions`,
  `needsGradingCount` (teachers), `submissionsConnection`.
- Top-level `assignment(id:)` accepts numeric or global ID.

### Submissions

- `assignment(id:) { submissionsConnection }` — for students this returns only
  their own submission (visibility is enforced server-side); teachers get all.
- Top-level `submission(assignmentId:, userId:)` needs an explicit user id.
- Submission fields: `_id`, `state` (submitted|unsubmitted|graded|pending_review|deleted),
  `submissionStatus`, `gradingStatus`, `score`, `grade`, `enteredScore`,
  `enteredGrade`, `excused`, `late`, `missing`, `secondsLate`, `submittedAt`,
  `gradedAt`, `postedAt`, `posted`, `cachedDueDate`, `attempt`,
  `submissionType`, `deductedPoints`, `redoRequest`, `user { _id name }`,
  `assignment { _id name }`.

### Grades / enrollments

- `course(id:) { enrollmentsConnection(filter: { userIds, types, states }) { nodes { ... } } }`
  Requires read_roster/read_grades. **Do not assume students are auto-scoped**:
  omitting `userIds` can still return the full student roster (names) to a
  student token, even when other students' `grades` fields are null. Always
  pass `userIds: [<self>]` unless `course.permissions.viewAllGrades` or
  `manageGrades` is true.
- Check grade scope via `course(id:) { permissions { viewAllGrades manageGrades } }`.
- Enrollment fields: `_id`, `type` (StudentEnrollment...), `state`,
  `user { _id name }`, `grades { currentScore currentGrade finalScore
  finalGrade unpostedCurrentScore unpostedCurrentGrade overrideScore overrideGrade }`.
- `grades(gradingPeriodId:)` defaults to the current grading period.

### Announcements / discussions

- `course(id:) { discussionsConnection(filter: { isAnnouncement: true, searchTerm, userId }) }`
- Discussion fields: `_id`, `title`, `message` (HTML), `postedAt`,
  `delayedPostAt`, `isAnnouncement`, `contextName`, `author { name }`.
- REST alternative for multi-course queries: `GET /api/v1/announcements?context_codes[]=course_123`
  (defaults to last 14 days; `start_date`/`end_date`/`latest_only` params).
- **Discussion topics (REST)**: `GET /api/v1/courses/:course_id/discussion_topics`
  lists topics (`only_announcements=false`, optional `search_term`, `order_by`,
  `scope`, `filter_by`). `GET .../discussion_topics/:topic_id` returns one topic
  including `message` HTML, `require_initial_post`, `user_can_see_posts`,
  `locked_for_user`, and `lock_explanation`. `GET .../discussion_topics/:topic_id/view`
  returns threaded `view` entries plus `participants` and `unread_entries`; may
  respond `403` with body `require_initial_post` when the user must post before
  viewing replies.
- **Quizzes (REST, classic)**: `GET /api/v1/courses/:course_id/quizzes` and
  `GET .../quizzes/:id` return metadata only (due dates, time limits, attempt
  policy, lock state, `question_count`, `question_types` labels). Optional
  `search_term` on list. Tools strip `access_code` and expose
  `requires_access_code` instead; `ip_filter` becomes `has_ip_filter`. Does not
  fetch question text or answers. New Quizzes may use a separate API — classic
  endpoint is what most institutions still expose via this path.
- **Rubrics**: `GET /api/v1/courses/:course_id/assignments/:assignment_id`
  with `include[]=rubric` returns `rubric` (criteria + ratings),
  `rubric_settings.points_possible`, and `use_rubric_for_grading`. Does not
  include student assessment scores — those appear on submissions with
  `include[]=rubric_assessment` (see P3.4 submission feedback).
- **Submission feedback**: `GET
  /api/v1/courses/:course_id/assignments/:assignment_id/submissions/self` with
  `include[]=submission_comments` and `include[]=rubric_assessment` returns the
  current user's comments, rubric scores, and attachments. `get_submission_status`
  filters GraphQL `submissionsConnection` to the authenticated user so classmate
  submissions are never returned.
- **Unified search**: `search_course_content(course_id, query, content_types?,
  limit=10)` fans out to Canvas list endpoints with `search_term` / GraphQL
  `searchTerm` where available (pages, assignments, modules, announcements,
  files, quizzes, discussions) plus one syllabus fetch. Results are ranked
  locally (title match, token overlap, body frequency, recency tie-break) and
  return bounded snippets only — no full page bodies.

### REST-only endpoints needed by tools

- **Todo items**: `GET /api/v1/users/self/todo` — items with `type`
  ("grading" | "submitting"), embedded `assignment` (or `quiz` with
  `include[]=ungraded_quizzes`), `context_type`, `course_id`, `html_url`,
  `needs_grading_count` (grading items). `course_ids[]` filters.
- **Upcoming events**: `GET /api/v1/users/self/upcoming_events` — calendar
  events and assignments mixed; assignment entries carry an `assignment`
  object (`id`, `name`, `due_at`, `points_possible`, `html_url`,
  `course_id`) plus `context_code` like `course_12942`.
- **Planner items**: `GET /api/v1/planner/items` — student planner feed
  (assignments, quizzes, discussions, pages, notes, calendar events, etc.).
  Query params: `start_date`, `end_date` (inclusive, `yyyy-mm-dd` or ISO-8601),
  `context_codes[]=course_{id}` to scope to one course, `per_page` (default 10).
  Each item has `plannable_type`, `plannable_id`, `plannable` (title, `due_at`
  or `todo_date` for notes), `course_id`, `html_url`, optional `submissions`
  flags, and `planner_override` (`marked_complete`, `dismissed`). Tools
  normalize `plannable_type` to student-facing labels (`discussion_topic` →
  `discussion`, `wiki_page` → `page`, `planner_note` → `note`).
- **Calendar events**: `GET /api/v1/calendar_events` — dated calendar events
  and assignment due dates (`type` = `event` or `assignment`; the tool fetches
  both and merges). Params: `start_date`, `end_date`, `context_codes[]`
  (`course_{id}`, up to 10 per request). Without `context_codes[]`, Canvas
  defaults to the user's personal calendar only — `get_calendar_events` scopes
  to dashboard courses when `course_id` is omitted. Use `excludes[]=description`
  and `excludes[]=child_events` to keep list payloads small.
- **Dashboard / current courses**: `GET /api/v1/dashboard/dashboard_cards` —
  the courses shown on the Canvas dashboard. Prefer this over
  `GET /api/v1/courses?enrollment_state=active`, which can still include
  concluded or open-ended enrollments that are not on the dashboard. Use
  `include[]=concluded` on courses if you need the concluded flag explicitly.
- **Modules**: `GET /api/v1/courses/:course_id/modules`,
  `.../modules/:module_id/items`, `.../items/:id`. Optional `search_term` on
  list endpoints. For structure-only listing, do **not** pass
  `include[]=items` (Canvas may omit large item arrays anyway — always be
  prepared to call List Module Items). Request `include[]=content_details` only
  on single-item show (or when intentionally expanding items) for points,
  due/lock dates, and lock_explanation. Student callers get module `state` /
  `completed_at` and `completion_requirement.completed` on items when
  applicable.   Item `type` is one of File, Page, Discussion, Assignment, Quiz,
  SubHeader, ExternalUrl, ExternalTool.
- **Syllabus**: `GET /api/v1/courses/:course_id` with `include[]=syllabus_body`
  returns `syllabus_body` (HTML). `syllabus_course_summary` may appear on the
  course object when Canvas exposes it (controls whether the assignment/calendar
  summary block is shown on the syllabus page).
- **Pages**: `GET /api/v1/courses/:course_id/pages` lists wiki pages (metadata
  only by default; optional `search_term`, `sort`, `order`). `GET
  /api/v1/courses/:course_id/pages/:url_or_id` returns a single page including
  `body` HTML. Accepts a url slug or numeric id — for ids use the
  `page_id:{id}` form when ambiguous. `get_page` also returns `body_text`
  (plain text via `html_to_text`).
- **Files / folders**: `GET /api/v1/courses/:course_id/files` and
  `.../folders`; `GET /api/v1/folders/:folder_id/files`;
  `GET /api/v1/files/:id`. List endpoints support `search_term` and
  `content_types[]` (MIME filter, e.g. `application/pdf` or `image`). Course
  folders returns a **flat** list of all subfolders. File objects use
  `content-type` (hyphenated) in JSON; responses include authenticated
  `url` download links but tools return metadata only (no local download).
- **File downloads**: use the `url` from file metadata with Bearer auth (Canvas
  often also includes a `verifier` query param). Local saves go under
  `CANVAS_DOWNLOAD_DIR`; only relative subfolders are allowed from tools.
  Downloads stream to disk via `download_file_to_path` with a
  `CANVAS_MAX_DOWNLOAD_SIZE_MB` cap (default 100). The initial download URL
  must be `https` on the same host as `CANVAS_BASE_URL`; duplicate local
  filenames get numeric suffixes (`file (1).pdf`). Batch downloads report
  per-file failures in `failed` without aborting the rest.
- **HTML utilities** (`src/canvas_mcp_server/utils/html.py`):
  - `html_to_text(html)` — plain text for LLM consumption; strips `script`/`style`.
  - `extract_canvas_links(html)` — `{href, text}` for every `<a>` tag.
  - `extract_canvas_resource_references(html)` — ordered resource dicts with
    `type` (`file`, `page`, `assignment`, `discussion`, `quiz`, `module`,
    `folder`, `external_url`), `id`, `course_id`, `url`, `label`. Detects
    course-relative Canvas paths and `data-api-endpoint` instructure embeds.
    Used by upcoming Pages and `get_assignment_resources` tools; file downloads
    reuse this via `extract_file_ids_from_html`.
- **Assignment resources**: `get_assignment_resources(course_id, assignment_id)`
  parses assignment description HTML via the shared html utils (anchor hrefs and
  `data-api-endpoint` instructure embeds). Returns deduped metadata for files,
  pages, external URLs, and other course objects — use before
  `download_assignment_files` when you need discovery separate from download.
- **Module downloads**: `download_module_files(course_id, module_id)` calls
  `get_module_items` and downloads only items where `type == "File"` (uses each
  item's `content_id` as the Canvas file id). **Does not** download Page,
  Assignment, Quiz, Discussion, ExternalUrl, or SubHeader items. Wiki page
  content is available via `get_page`; assignment bodies via `get_assignment_details`.
  Post-v1 candidates: `export_page` (save page HTML/text to disk),
  `download_module_content` (batch all module item types).
- **Missing submissions**: `GET /api/v1/users/:user_id/missing_submissions`.

## 6. Looking up more documentation (for future tools)

- Full index: <https://developerdocs.instructure.com/llms.txt>
  (complete corpus: `llms-full.txt`).
- Any docs page is available as Markdown by appending `.md` to its URL.
- Docs can be queried in natural language:
  `GET https://developerdocs.instructure.com/get_started.md?ask=<question>&goal=<endgoal>`
- Resource pages follow `https://developerdocs.instructure.com/services/canvas/resources/<name>.md`
  — e.g. `assignments.md`, `submissions.md`, `users.md`, `enrollments.md`,
  `enrollment_terms.md`, `modules.md`, `announcements.md`, `calendar_events.md`,
  `quizzes.md`, `discussion_topics.md`, `files.md`, `sections.md`, `planner.md`.
  Basics pages: `services/canvas/basics/file.<topic>.md` (graphql, pagination,
  throttling, sis_ids, masquerading, file_uploads...). OAuth pages:
  `services/canvas/oauth2/file.oauth.md`, `file.developer_keys.md`,
  `file.oauth_endpoints.md`.
