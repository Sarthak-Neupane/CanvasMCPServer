# Canvas MCP error model

Every MCP tool in this server returns either a **success payload** (a Pydantic
model or list of models) or a **structured error object** with a stable schema.
Agents should branch on `code` and `retryable`; humans can read `title` and
`message`.

## Error response schema

When a tool fails, it returns a JSON object with these fields:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `code` | string | yes | Stable machine-readable identifier (see catalog below). |
| `message` | string | yes | Detailed explanation suitable for the user or agent. |
| `title` | string | yes | Short category label (e.g. `Not Found`). |
| `error` | string | yes | **Legacy alias** of `title` — kept for backward compatibility. |
| `retryable` | boolean | yes | Whether the same request may succeed if retried later. |
| `status_code` | integer | no | HTTP status from Canvas when the failure came from an API call. |
| `source` | string | no | Where the failure originated: `local`, `canvas_rest`, `canvas_graphql`, or `download`. |
| `details` | object | no | Structured context (ids, lock reasons, etc.). |
| `lock_reason` | string | no | Promoted from `details` for discussion lock errors. |
| `file_id` | string | no | Promoted from `details` for single-file download failures. |

Example (rate limited):

```json
{
  "code": "canvas_rate_limited",
  "title": "Rate Limited",
  "error": "Rate Limited",
  "message": "Canvas API rate limit exceeded. Retry the request later.",
  "status_code": 429,
  "retryable": true,
  "source": "canvas_graphql"
}
```

Example (discussion locked):

```json
{
  "code": "discussion_locked",
  "title": "Discussion Locked",
  "error": "Discussion Locked",
  "message": "You must post a reply before viewing other posts in this discussion.",
  "status_code": 403,
  "retryable": false,
  "source": "canvas_rest",
  "lock_reason": "require_initial_post",
  "details": {
    "lock_reason": "require_initial_post"
  }
}
```

## Error code catalog

| Code | Title | Retryable | When it happens |
| --- | --- | --- | --- |
| `config_missing` | Configuration Error | no | Required env vars (`CANVAS_API_TOKEN`, `CANVAS_BASE_URL`) are missing. |
| `config_invalid` | Configuration Error | no | Env vars are present but invalid. |
| `canvas_unauthorized` | Authentication Failed | no | Canvas rejected the token (HTTP 401). |
| `canvas_forbidden` | Access Forbidden | no | Valid token but insufficient permission (HTTP 403). |
| `invalid_argument` | Invalid Argument | no | Local validation failed (path traversal, unknown search type, etc.). |
| `invalid_request` | Invalid Request | no | Request rejected as invalid by Canvas (HTTP 400) or tool input rules. |
| `resource_not_found` | Not Found | no | Resource missing or not visible (HTTP 404). |
| `canvas_bad_request` | Bad Request | no | Canvas HTTP 400. |
| `canvas_rate_limited` | Rate Limited | **yes** | Canvas HTTP 429. Honor `Retry-After` when present (see retry policy). |
| `canvas_unavailable` | Canvas Unavailable | **yes** | Canvas HTTP 5xx. |
| `request_timeout` | Request Timeout | **yes** | HTTP request timed out. |
| `network_error` | Network Error | **yes** | Transport failure contacting Canvas. |
| `graphql_error` | GraphQL Error | no | Canvas GraphQL returned errors in the response body. |
| `unexpected_response` | Unexpected Response | no | Canvas returned JSON the tool could not parse or validate. |
| `unexpected_error` | Unexpected Error | no | Unhandled internal failure. |
| `download_failed` | Download Error | no | A file download failed after metadata was resolved. |
| `download_too_large` | Download Error | no | File exceeds `CANVAS_MAX_DOWNLOAD_SIZE_MB`. |
| `download_url_rejected` | Download Error | no | Download URL failed host/scheme validation. |
| `resource_course_mismatch` | Resource Course Mismatch | no | The requested file belongs to a different course than specified. |
| `discussion_locked` | Discussion Locked | no | `require_initial_post` — post before viewing replies. |
| `discussion_unavailable` | Discussion Unavailable | **yes** | Discussion view not built yet (HTTP 503). |
| `rubric_not_found` | Not Found | no | Assignment exists but has no rubric attached. |

## Agent guidance

1. **Check `code` first** — it is stable across releases; `message` text may change.
2. **Respect `retryable`** — when `true`, wait (exponential backoff for 429/5xx)
   and retry the same tool call. When `false`, fix inputs, permissions, or
   choose a different tool.
3. **Do not retry** `canvas_unauthorized` or `canvas_forbidden` without user
   action (new token or different resource).
4. **Batch downloads** (`download_course_files`, etc.) return `DownloadBatchResult`
   on success with per-file failures in `failed[]`; only top-level discovery
   errors use this schema.

## Implementation

- Model: `src/canvas_mcp_server/errors/tool_error.py` (`ToolError`)
- Codes: `src/canvas_mcp_server/errors/codes.py` (`ErrorCode`, `ERROR_DEFINITIONS`)
- Mappers: `src/canvas_mcp_server/errors/mappers.py` (`as_tool_error`, `tool_error_from_http`)
- Tools call `as_tool_error(exception, source=...)` in a single `except Exception` block.

HTTP-layer retries (429/5xx/network) are handled inside the Canvas client before
errors surface to tools; tool-level `retryable` tells agents whether a **second
tool invocation** may help.
