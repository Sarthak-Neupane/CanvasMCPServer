# Security & privacy

This document describes how **Canvas MCP Server** handles secrets, untrusted
content, and student data. It applies to the student read-only v1 tool set.

## Threat model

The server runs locally, speaks MCP over stdio, and calls Canvas with a
personal API token. Primary risks:

1. **Token leakage** — bearer tokens in logs, errors, or tool output.
2. **HTML execution** — Canvas pages/assignments/discussions contain HTML that
   must never be executed in this process.
3. **Student data scope** — grades and submissions must never expose classmates'
   records to a student-scoped token.

## Canvas HTML is untrusted

Canvas returns user- and institution-authored HTML in pages, assignments,
syllabi, discussions, announcements, and quizzes. This server:

- Converts HTML to **plain text** via `html_to_text()` for agent consumption.
- **Never executes** HTML, JavaScript, embedded objects, or iframes.
- Strips content inside `script`, `style`, `noscript`, `iframe`, `object`,
  `embed`, `template`, `svg`, and `canvas` tags.
- Ignores `javascript:`, `vbscript:`, and `data:` link targets when extracting
  links.

Content-bearing tool responses include provenance fields (`source_type`,
`course_id`, `resource_id`, `canvas_url`) so agents can treat bodies as
untrusted text and link back to Canvas when needed.

## Token protection

- API tokens are read from `CANVAS_API_TOKEN` (or OAuth in future) and sent only
  in the `Authorization` header to Canvas.
- Error messages and URLs are passed through `redact_sensitive_text()` /
  `redact_url()` so bearer tokens and `access_token` query parameters do not
  appear in `HTTPError` strings or the server's top-level error print path.
- Do not commit `.env`, tokens, or institution-specific IDs. Rotate any token
  that was ever committed.

## Student privacy invariant

**A student-scoped token must only receive the authenticated user's own grades
and submissions.** Classmate roster data from Canvas must not be forwarded even
when Canvas returns it.

Enforcement:

| Area | Tool(s) | Behavior |
| --- | --- | --- |
| Submissions | `get_submission_status` | GraphQL query scoped to `users/self`; response filtered to self |
| Grades | `get_course_grades` | Student path queries only self; roster rows from Canvas are dropped |
| Discussions | `get_discussion_entries` | Returns thread content visible to the user; no separate roster tool |
| Peer review | (planner labels only) | No dedicated peer-review roster export tool in v1 |
| Groups | — | No group-membership export tool in v1 |

Automated regression tests: `tests/test_privacy.py` (marker: `privacy`). Run:

```bash
uv run pytest -m privacy
```

## Read-only guarantee (v1)

This server is **student read-only** for Canvas data:

- **No** create, update, or delete calls to Canvas (no submission upload, grade
  change, discussion post, etc.).
- The only local writes are **`download_*` tools**, which save Canvas-hosted
  files under `CANVAS_DOWNLOAD_DIR` (default `~/Downloads/Canvas`).
- Agents should use detail tools for page/assignment HTML; downloads are for
  binary files only.

## Download safety

- Download URLs must match the configured `CANVAS_BASE_URL` host (HTTPS).
- Paths are sanitized; `folder` parameters cannot be absolute or contain `..`.
- Single-file size capped by `CANVAS_MAX_DOWNLOAD_SIZE_MB` (default 100).
- Streams to disk — full file is not held in memory.

## Reporting issues

If you find a security or privacy bug, please open a GitHub issue with minimal
reproduction steps. Do not include real API tokens or student PII.
