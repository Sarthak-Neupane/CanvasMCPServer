# Clean install validation (P9.6)

Manual checklist before tagging **student-readonly-v1**. Automated CI covers
formatting, types, and mocked tests; this document covers first-time install on
a fresh machine and MCP client wiring.

## Prerequisites (all platforms)

- [ ] Python 3.13+ installed (`python3 --version`)
- [ ] `uv` installed (`uv --version`)
- [ ] Git clone of this repository
- [ ] Canvas API token from your institution (Account → Settings → Approved Integrations)
- [ ] Institution `CANVAS_BASE_URL` ending in `/api` (not `/api/v1`)

## P9.6.1 — macOS fresh install

```bash
git clone https://github.com/sarthakneupane/canvas-mcp-server.git
cd canvas-mcp-server
uv sync --extra dev
cp .env.example .env
# Edit .env with CANVAS_API_TOKEN and CANVAS_BASE_URL
CANVAS_API_TOKEN= CANVAS_BASE_URL= uv run pytest   # should pass without .env
uv run mypy src/ --strict
uv run canvas-mcp-server   # should print "Starting Canvas MCP Server..." on stderr
```

- [ ] `uv sync` completes without errors
- [ ] `pytest` passes (188+ tests)
- [ ] Server starts without crashing (Ctrl+C to stop)
- [ ] With real `.env`, Cursor can list courses (see P9.6.3)

## P9.6.2 — Windows fresh install

Use **Git Bash**, **WSL**, or **PowerShell** with Python 3.13+ and uv installed.

```powershell
git clone https://github.com/sarthakneupane/canvas-mcp-server.git
cd canvas-mcp-server
uv sync --extra dev
copy .env.example .env
# Edit .env
$env:CANVAS_API_TOKEN=""; $env:CANVAS_BASE_URL=""; uv run pytest
```

- [ ] `uv sync` completes
- [ ] `pytest` passes
- [ ] MCP config uses the Windows path to `.venv\Scripts\canvas-mcp-server.exe`
  (or `uv run` wrapper — see below)

**Windows MCP command example:**

```json
{
  "mcpServers": {
    "canvas": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\path\\to\\canvas-mcp-server",
        "run",
        "canvas-mcp-server"
      ]
    }
  }
}
```

## P9.6.3 — Cursor + Claude Desktop MCP wiring

### Cursor

File: `~/.cursor/mcp.json` or project `.cursor/mcp.json`

```json
{
  "mcpServers": {
    "canvas": {
      "command": "/absolute/path/to/canvas-mcp-server/.venv/bin/canvas-mcp-server"
    }
  }
}
```

- [ ] MCP server shows as connected in Cursor Settings → MCP
- [ ] Prompt: *"List my current courses"* → returns course names
- [ ] Prompt: *"What's on my todo list?"* → returns todo items
- [ ] Reload MCP after pulling code changes

### Claude Desktop

Add the same server block to the Claude Desktop MCP config for your OS.

- [ ] Server connects without token appearing in logs
- [ ] A simple course query succeeds

## Smoke prompts (optional quick check)

| Prompt | Expected tool(s) |
| --- | --- |
| List my dashboard courses | `get_all_courses` (`active_only=true`) |
| What assignments are due this week? | `get_calendar_events` / `get_planner_items` |
| Show modules for course X | `get_course_modules` |

Full acceptance suite: Phase 10 in [student-readonly-v1-roadmap.md](student-readonly-v1-roadmap.md).

## Sign-off

| Check | macOS | Windows | Notes |
| --- | --- | --- | --- |
| `uv sync --extra dev` | | | |
| `pytest` (no token) | | | |
| MCP connects | | | |
| Live course query | | | |

Date: __________   Tester: __________
