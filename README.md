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
| `get_all_courses` | List courses for the current user (id, name, course code, term). Set `active_only=true` for just your current courses (what shows on the Canvas dashboard). Optional `term` filter, e.g. `"Fall 2025"`. |
| `get_course_by_id` | Get details for a single course by numeric ID or GraphQL global ID. |
| `get_upcoming_assignments` | List upcoming assignments across all courses with due dates and points. |
| `get_assignments_for_course` | List all assignments in a course (name, due date, points, state, URL). |
| `get_assignment_details` | Get one assignment's description, due/lock dates, grading type, submission types, and allowed attempts. |
| `get_todo_items` | List the user's todo items: assignments to submit (students) or grade (teachers). |
| `get_submission_status` | Check submission status for an assignment: submitted/late/missing, score and grade. Students see their own; teachers see all. |
| `get_course_grades` | Get current and final scores/grades for a course. Students see their own; teachers see all students. |
| `get_announcements` | List a course's announcements (title, message, post date, author). |

Course, assignment, submission, grade, and announcement data comes from the
[Canvas GraphQL API](https://developerdocs.instructure.com/services/canvas/basics/file.graphql);
todo items and upcoming assignments use the REST API since GraphQL does not
expose them.

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

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `CANVAS_API_TOKEN` | yes | — | Canvas API access token |
| `CANVAS_BASE_URL` | yes | — | Your institution's Canvas API base URL (must end at `/api`) |
| `CANVAS_TIMEOUT` | no | `30` | Request timeout in seconds |
| `DEBUG` | no | `false` | Enable debug mode |
| `LOG_LEVEL` | no | `INFO` | Log level |

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
uv sync                          # install dependencies (incl. dev tooling via pip extras)
uv run python scripts/run_server.py   # run the dev server

uv run pytest                    # tests
uv run black src/ tests/         # formatting
uv run isort src/ tests/
uv run mypy src/ --strict        # type checking
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
