"""Ensure registered MCP tools stay documented."""

from __future__ import annotations

import re
from pathlib import Path

from canvas_mcp_server.tools import ALL_TOOLS

TOOLS_DOC = Path(__file__).resolve().parents[1] / "docs" / "tools.md"
TOOL_NAME_RE = re.compile(r"`([a-z_]+)`")


def test_all_tools_listed_in_docs() -> None:
    doc_text = TOOLS_DOC.read_text(encoding="utf-8")
    documented = set(TOOL_NAME_RE.findall(doc_text))
    registered = {tool.name for tool in ALL_TOOLS}

    missing = sorted(registered - documented)
    assert not missing, f"Tools missing from docs/tools.md: {missing}"
