# Canvas MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that lets AI
assistants (Cursor, Claude Desktop, and any other MCP client) query your
[Canvas LMS](https://www.instructure.com/canvas) data — courses, terms, and more —
through the [Canvas GraphQL API](https://developerdocs.instructure.com/services/canvas/basics/file.graphql).

## Features

- Query Canvas via GraphQL (single request, no REST pagination juggling)
- Typed responses validated with Pydantic models
- Structured error reporting (auth failures, rate limits, missing resources)
- Runs over stdio — works with any MCP client
- Graceful shutdown on SIGINT/SIGTERM

## Available Tools

| Tool | Description |
| --- | --- |
| `get_all_courses` | List courses for the current user (id, name, course code, term). Set `active_only=true` for dashboard courses only (stricter than `enrollment_state=active`). Optional `term` filter, e.g. `"Fall 2025"`. |
| `get_course_by_id` | Get details for a single course by numeric ID or GraphQL global ID. |
| `get_course_syllabus` | Get a course syllabus (`syllabus_body` HTML) for policy, grading, and exam rules. |
| `get_course_pages` | List wiki pages in a course (title, url slug, publish state). Optional `search_term`. |
| `get_page` | Get one wiki page by slug, numeric id, or full Canvas path (HTML + plain `body_text`). |
| `get_course_files` | List course files with metadata (name, MIME type, size, download URL). Optional `search_term` and `content_type`. |
| `get_course_folders` | List all folders in a course (flat list with full paths and file counts). |
| `get_folder_files` | List files in a folder by `folder_id`. Optional `search_term` and `content_type`. |
| `get_file_details` | Get metadata for one file by `file_id` (includes download URL; does not download). |
| `download_file` | Download one Canvas **file** to `CANVAS_DOWNLOAD_DIR` (default `~/Downloads/Canvas/{course}/{folder?}/`). |
| `download_course_files` | Download course **files** matching optional `search_term` / `content_type` filters. |
| `download_module_files` | Download **File-type module items only** (Canvas-hosted files). Skips Pages, Assignments, Quizzes, and external links — use `get_page` / `get_assignment_details` for those. |
| `download_assignment_files` | Download **files embedded** in an assignment description (via `get_assignment_resources` discovery). Optional relative `folder`. |
| `get_upcoming_assignments` | List upcoming assignments across all courses with due dates and points. |
| `get_assignments_for_course` | List all assignments in a course (name, due date, points, state, URL). |
| `get_assignment_details` | Get one assignment's description, due/lock dates, grading type, submission types, and allowed attempts. |
| `get_assignment_resources` | Discover files, pages, and external URLs linked in an assignment description (metadata only). |
| `get_todo_items` | List the user's todo items: assignments to submit (students) or grade (teachers). |
| `get_planner_items` | List student planner items (assignments, quizzes, discussions, pages, notes) with optional date/course filters. |
| `get_calendar_events` | List calendar events and assignment due dates with optional date/course filters. |
| `get_course_discussions` | List discussion topics in a course (lock state, initial-post requirement). Optional `search_term`. |
| `get_discussion` | Get one discussion topic including prompt HTML and lock metadata. |
| `get_discussion_entries` | List threaded replies in a discussion; clear error when initial post is required. |
| `get_course_quizzes` | List quizzes in a course (metadata only: due dates, time limits, lock state). Optional `search_term`. |
| `get_quiz` | Get one quiz by id (instructions and settings; no questions). |
| `get_assignment_rubric` | Get an assignment's rubric criteria and rating levels (no student scores). |
| `get_submission_status` | Check your submission status for an assignment: submitted/late/missing, score and grade. Self only. |
| `get_submission_feedback` | Get instructor feedback on your submission: comments, rubric scores, attachments. Self only. |
| `search_course_content` | Search a course across syllabus, pages, assignments, modules, announcements, files, quizzes, and discussions. |
| `get_course_grades` | Get current and final scores/grades for a course. Students see only their own enrollment (no classmate roster); teachers with grade permission see all students. |
| `get_announcements` | List a course's announcements (title, message, post date, author). |
| `get_course_modules` | List modules in a course (structure only: name, position, unlock date, item count, student progression). Optional `search_term`. |
| `get_module_items` | List items in a module (File, Page, Assignment, Quiz, etc.) with completion requirements. Optional `search_term`. |
| `get_module_item_details` | Get one module item with `content_details` (points, due/lock dates, lock explanation). |

Course, assignment, submission, grade, and announcement data comes from the
[Canvas GraphQL API](https://developerdocs.instructure.com/services/canvas/basics/file.graphql);
todo items, upcoming assignments, dashboard (`active_only`) course lists, planner,
calendar events, discussions, quizzes, rubrics, unified course search, modules,
syllabi, pages, and files/folders use the REST API where GraphQL does not expose them (or where REST is
the accurate source of truth).

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- A Canvas API access token

## Installation

```bash
git clone https://github.com/sarthakneupane/canvas-mcp-server.git
cd canvas-mcp-server
uv sync            # creates .venv and installs everything from uv.lock
```

Or with pip:

```bash
pip install -e .
```

## Configuration

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env`:

   ```bash
   CANVAS_API_TOKEN=your_actual_api_token_here
   CANVAS_BASE_URL=https://your-school.instructure.com/api
   ```

   - **Token**: generate one in Canvas under Account → Profile → Approved
     Integrations → "New Access Token". Treat it like a password.
   - **Base URL**: must end at `/api` (not `/api/v1`) — the server posts GraphQL
     queries to `{CANVAS_BASE_URL}/graphql`. Use **your own institution's**
     Canvas domain: it is the URL you see in the browser when you log in to
     Canvas, with `/api` appended. Most schools use
     `https://<your-school>.instructure.com`, while some use a custom domain
     such as `https://canvas.<your-school>.edu` — use whichever one you log in
     with. The public Free-for-Teacher instance (`canvas.instructure.com`) was
     [permanently discontinued in 2026](https://www.instructure.com/incident-update/customers),
     so an institution domain is required.

   - **Downloads**: files are saved under `CANVAS_DOWNLOAD_DIR` (default
     `~/Downloads/Canvas`), organized as `{course_name}/{optional_folder}/{filename}`.
     Tools accept only a relative `folder` name — never an absolute path.
     Download tools save **Canvas Files** only (binary uploads). They do not
     export wiki Pages, assignment HTML, or other module item types — use
     `get_page`, `get_assignment_details`, or `get_assignment_resources` to read
     that content in the chat instead. Downloads stream to disk (not fully
     buffered in memory), enforce `CANVAS_MAX_DOWNLOAD_SIZE_MB`, validate that
     file URLs match your `CANVAS_BASE_URL` host, and suffix duplicate filenames
     (e.g. `notes (1).pdf`).

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `CANVAS_API_TOKEN` | yes | — | Canvas API access token |
| `CANVAS_BASE_URL` | yes | — | Your institution's Canvas API base URL (must end at `/api`) |
| `CANVAS_TIMEOUT` | no | `30` | Request timeout in seconds |
| `CANVAS_DOWNLOAD_DIR` | no | `~/Downloads/Canvas` | Root directory for downloaded files |
| `CANVAS_DOWNLOAD_TIMEOUT` | no | same as `CANVAS_TIMEOUT` | Timeout for binary file downloads |
| `CANVAS_MAX_DOWNLOAD_SIZE_MB` | no | `100` | Maximum size (MB) for a single file download |
| `CANVAS_MAX_RETRIES` | no | `3` | Retries after the first attempt for 429/5xx/network errors |
| `CANVAS_RETRY_BASE_DELAY` | no | `1.0` | Base seconds for exponential backoff between retries |
| `DEBUG` | no | `false` | Enable debug mode |
| `LOG_LEVEL` | no | `INFO` | Log level |

## Tool errors

On failure, every tool returns a **structured error object** instead of raising.
Agents should branch on `code` and `retryable`; `error` is a legacy alias of
`title`.

| Field | Meaning |
| --- | --- |
| `code` | Stable identifier (e.g. `resource_not_found`, `canvas_rate_limited`) |
| `message` | Detailed explanation |
| `title` / `error` | Short category label |
| `retryable` | Whether to retry the same tool call later |
| `status_code` | Canvas HTTP status when applicable |
| `source` | `local`, `canvas_rest`, `canvas_graphql`, or `download` |

Common codes: `canvas_unauthorized` (401), `canvas_forbidden` (403),
`resource_not_found` (404), `canvas_rate_limited` (429, retryable),
`canvas_unavailable` (5xx, retryable), `invalid_argument` (bad tool input),
`discussion_locked` (`require_initial_post`), `download_failed`.

Full catalog and agent guidance: [docs/errors.md](docs/errors.md).

## Output conventions

List tools return a `ListResult` object (`results`, `result_count`, `truncated`)
instead of a bare array. GraphQL-backed models use **camelCase**; REST-backed
models use **snake_case**. Timestamps serialize as ISO-8601; nullable fields
serialize as JSON `null`.

Details: [docs/output-conventions.md](docs/output-conventions.md).

## Security & privacy

Canvas HTML is converted to plain text and **never executed** in this server.
Content tools attach provenance metadata (`source_type`, `course_id`,
`resource_id`, `canvas_url`) so agents can treat bodies as untrusted. API
tokens are redacted from error strings and URLs where possible.

Student-scoped tokens only receive the authenticated user's grades and
submissions; classmate roster leaks from Canvas are filtered out.

Details: [SECURITY.md](SECURITY.md). Privacy regression tests:
`uv run pytest -m privacy`.

## Usage

### Standalone

```bash
uv run canvas-mcp-server
```

The server communicates over stdio (stdin/stdout JSON-RPC); it is meant to be
launched by an MCP client rather than used interactively.

### With Cursor

Add to `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (per-project), using
the absolute path to your clone:

```json
{
  "mcpServers": {
    "canvas": {
      "command": "/absolute/path/to/canvas-mcp-server/.venv/bin/canvas-mcp-server"
    }
  }
}
```

Then refresh MCP servers in Cursor Settings and ask e.g. *"list my Fall 2025 courses"*.

### With Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "canvas": {
      "command": "/absolute/path/to/canvas-mcp-server/.venv/bin/canvas-mcp-server"
    }
  }
}
```

## Development

```bash
uv sync --extra dev               # install runtime + dev deps (pytest, respx, …)
uv run python scripts/run_server.py   # run the dev server

uv run pytest                    # run tests (mocked Canvas — no live token needed)
uv run black src/ tests/         # formatting
uv run isort src/ tests/
uv run mypy src/ --strict        # type checking
```

Tests use mocked Canvas responses (`tests/fixtures/`, `tests/helpers/canvas_mock.py`).
No `CANVAS_API_TOKEN` or `.env` file is required — CI and local runs use empty
credentials:

```bash
CANVAS_API_TOKEN= CANVAS_BASE_URL= uv run pytest
```

## Project Structure

```
canvas-mcp-server/
├── src/canvas_mcp_server/
│   ├── server.py          # FastMCP server setup, tool registration, entry point
│   ├── config.py          # Environment configuration (.env)
│   ├── tools/courses/     # MCP tools (one file per tool)
│   ├── models/courses/    # Pydantic models for Canvas responses
│   ├── constants/         # Canvas enums (workflow states, enrollment types, ...)
│   └── utils/             # HTTP + Canvas GraphQL client
├── docs/                  # Canvas API reference notes
├── scripts/               # Development scripts
└── tests/                 # Test suite
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make your changes — keep commits small and feature-scoped
4. Run tests (`uv run pytest`) and type checks (`uv run mypy src/ --strict`)
5. Open a Pull Request

Never commit `.env` or real API tokens. See `docs/canvas-api-knowledge.md` for a
summary of the Canvas API used by this project.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Author

**Sarthak Neupane**

- GitHub: [@Sarthak-Neupane](https://github.com/Sarthak-Neupane)
