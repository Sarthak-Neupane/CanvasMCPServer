# Architecture

Canvas MCP Server is a **stdio MCP adapter** between AI clients and the Canvas
LMS APIs. It does not expose an HTTP server; the MCP host (Cursor, Claude
Desktop, etc.) launches `canvas-mcp-server` as a subprocess and exchanges
JSON-RPC messages over stdin/stdout.

## Layer diagram

```text
┌─────────────────────────────────────────────────────────────┐
│  MCP host (Cursor / Claude Desktop / other MCP client)      │
└───────────────────────────┬─────────────────────────────────┘
                            │ stdio (JSON-RPC)
┌───────────────────────────▼─────────────────────────────────┐
│  server.py          FastMCP registration, signal handling     │
│  tools/*            One module per MCP tool (async handlers)  │
│  models/*           Pydantic response / request shapes      │
│  errors/*           Structured ToolError + HTTP mappers       │
│  constants/*        Canvas enums shared by models             │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│  utils/canvas_api.py    Singleton client (REST + GraphQL)     │
│  utils/http_client.py   httpx, retries, redacted errors       │
│  utils/graphql*.py      Relay pagination, response extract    │
│  utils/rest_pagination  Link-header page walking              │
│  utils/html.py          HTML → plain text (never execute)     │
│  utils/file_download.py Local file writes + URL validation    │
│  utils/list_limits.py   Shared list `limit` / truncation      │
│  utils/token_cache.py   Per-token TTL cache (dashboard, self) │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTPS
┌───────────────────────────▼─────────────────────────────────┐
│  Canvas LMS  {CANVAS_BASE_URL}/graphql  +  /api/v1/...       │
└─────────────────────────────────────────────────────────────┘
```

## Request flow (happy path)

1. MCP host invokes a tool by name with JSON arguments.
2. FastMCP calls the registered async function in `tools/`.
3. The tool calls `canvas_api_client` (`get_rest`, `get_rest_paginated`,
   `post_graphql_query`, or `download_file_to_path`).
4. HTTP layer applies retry policy (429/5xx), attaches `Authorization: Bearer`.
5. Raw JSON is validated into Pydantic models (or wrapped in `ListResult`).
6. The model is serialized to JSON and returned to the MCP host.

On failure, tools catch exceptions and return `as_tool_error(...).to_response()`
so agents always get a dict with `code`, `message`, and `retryable`.

## GraphQL vs REST

| Use GraphQL when | Use REST when |
| --- | --- |
| Field exists in GraphQL schema | GraphQL schema is missing the resource |
| Single connection query fits (courses, assignments, grades) | Endpoint is REST-only (todo, planner, calendar, modules, pages, files) |
| Relay pagination is sufficient | Link-header REST pagination is the documented API |
| camelCase matches Canvas GraphQL | snake_case matches Canvas REST JSON |

`CANVAS_BASE_URL` must end at `/api`. GraphQL posts to `{base}/graphql`; REST
uses `{base}/v1/...`.

The unified search tool (`search_course_content`) fans out to multiple REST and
GraphQL collectors, ranks locally, and returns snippets — it does not proxy a
single Canvas search endpoint.

## Tool conventions

- **Read-only v1:** no create/update/delete Canvas resources (downloads write
  only to the local `CANVAS_DOWNLOAD_DIR`).
- **List vs detail:** list tools return summaries and accept `limit`; detail
  tools return HTML bodies converted to `*_text` fields where applicable.
- **Student scope:** grades and submissions tools enforce self-only visibility
  even if Canvas returns broader data.
- **Errors:** never leak bearer tokens in strings; see `utils/redaction.py`.

## Configuration

`config.py` loads `.env` from the project root. Required: `CANVAS_API_TOKEN`,
`CANVAS_BASE_URL`. Optional: timeouts, download directory, retry counts.

## Testing strategy

- **Unit tests** mock Canvas via `tests/helpers/canvas_mock.py` — no network.
- **Fixtures** in `tests/fixtures/` mirror real Canvas JSON shapes.
- **Privacy tests** (`pytest -m privacy`) guard roster leaks.
- **Registry test** ensures every tool in `ALL_TOOLS` appears in `docs/tools.md`.

Manual acceptance against a live student account is documented in Phase 10 of
the [roadmap](student-readonly-v1-roadmap.md) and
[install-validation.md](install-validation.md).

## Related docs

- [tools.md](tools.md) — per-tool catalog
- [errors.md](errors.md) — error codes
- [output-conventions.md](output-conventions.md) — list shapes and naming
- [canvas-api-knowledge.md](canvas-api-knowledge.md) — Canvas API notes
- [SECURITY.md](../SECURITY.md) — threat model and privacy
