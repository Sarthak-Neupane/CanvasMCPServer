# Contributing to Canvas MCP Server

Thank you for helping improve the student read-only Canvas MCP server. This
project targets **read-only** student workflows: list/summarize course data,
fetch detail on demand, and optionally download Canvas-hosted files.

## Prerequisites

- Python **3.13+**
- [uv](https://docs.astral.sh/uv/) (recommended)
- A Canvas API token for manual testing (never commit it)

## Setup

```bash
git clone https://github.com/sarthakneupane/canvas-mcp-server.git
cd canvas-mcp-server
uv sync --extra dev
cp .env.example .env   # edit with your institution URL and token
```

## Development commands

```bash
uv run pytest                          # unit tests (mocked Canvas)
uv run pytest -m privacy               # privacy regression suite
uv run black src/ tests/               # format
uv run isort src/ tests/               # import order
uv run mypy src/ --strict              # types
uv run canvas-mcp-server               # run server (stdio)
```

Tests do **not** need a real token. CI and local runs use empty credentials:

```bash
CANVAS_API_TOKEN= CANVAS_BASE_URL= uv run pytest
```

## Architecture (short)

```
MCP client (Cursor, Claude Desktop)
        │ stdio JSON-RPC
        ▼
server.py  →  tools/*  →  models/*  (Pydantic)
                    │
                    ▼
            utils/canvas_api.py  →  Canvas REST / GraphQL
```

- **Tools** (`src/canvas_mcp_server/tools/`): one async function + `Tool` export per MCP tool.
- **Models** (`models/`): typed responses; GraphQL fields use camelCase, REST uses snake_case.
- **Errors** (`errors/`): `as_tool_error()` — tools return error dicts, never raise to MCP.
- **Utils** (`utils/`): HTTP client, pagination, HTML text extraction, downloads, retry policy.

Full design: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Adding a new tool

1. **Pick the API** — GraphQL when the field exists in schema; otherwise REST.
   See [docs/canvas-api-knowledge.md](docs/canvas-api-knowledge.md).

2. **Add a Pydantic model** under `models/<domain>/`.

3. **Implement the tool** in `tools/<domain>/get_*.py`:
   - Use `Annotated[..., Field(description=...)]` for parameters.
   - Return a model or `ListResult` on success; `as_tool_error()` on failure.
   - List tools: accept `limit` (use `ListLimitField` from `utils/list_limits`).
   - List tools: return **summaries** only; add or reuse a detail tool for HTML bodies.

4. **Register** — export `*_tool` from the domain `__init__.py` and append to
   `ALL_TOOLS` in `tools/__init__.py`.

5. **Test** — add fixtures under `tests/fixtures/`, tool tests under
   `tests/tools/`, using the `canvas_api` pytest fixture.

6. **Document** — add a row to [docs/tools.md](docs/tools.md) (enforced by
   `tests/test_tool_registry.py`).

7. **Commit** — one logical commit per feature; message explains *why*.

## Code style

- `black` + `isort` (profile black), line length 88.
- `mypy --strict` on `src/`.
- Match existing patterns in neighboring files; avoid drive-by refactors.
- No secrets in commits (`.env`, tokens, real course IDs).

## Pull requests

1. Branch from `main`.
2. Ensure CI passes locally (format, types, tests).
3. Update README / docs when behavior or setup changes.
4. Describe testing performed (unit tests required; note any manual Canvas checks).

## Security & privacy

Read [SECURITY.md](SECURITY.md) before touching grades, submissions, downloads,
or HTML handling. Privacy regressions: `uv run pytest -m privacy`.

## Questions

Open a [GitHub issue](https://github.com/sarthakneupane/canvas-mcp-server/issues)
for bugs or design discussion before large changes.
