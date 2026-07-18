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

## 5. Looking up more documentation (for future tools)

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
