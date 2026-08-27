"""Redact secrets from log and error output."""

from __future__ import annotations

import re
from typing import Any, Dict, Mapping, Optional
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

_BEARER_RE = re.compile(
    r"(Bearer\s+)([A-Za-z0-9._~+/=-]+)",
    re.IGNORECASE,
)
_ACCESS_TOKEN_PARAM_RE = re.compile(
    r"([?&]access_token=)([^&\s]+)",
    re.IGNORECASE,
)
_AUTHORIZATION_HEADER_RE = re.compile(
    r"(Authorization\s*[:=]\s*)(Bearer\s+)?([A-Za-z0-9._~+/=-]+)",
    re.IGNORECASE,
)
_REDACTED = "***REDACTED***"


def redact_sensitive_text(value: Optional[str]) -> str:
    """Remove bearer tokens and access_token query params from free text."""
    if not value:
        return ""
    redacted = _BEARER_RE.sub(rf"\1{_REDACTED}", value)
    redacted = _ACCESS_TOKEN_PARAM_RE.sub(rf"\1{_REDACTED}", redacted)
    redacted = _AUTHORIZATION_HEADER_RE.sub(
        lambda match: f"{match.group(1)}{match.group(2) or ''}{_REDACTED}",
        redacted,
    )
    return redacted


def redact_url(url: Optional[str]) -> Optional[str]:
    """Strip access_token from a URL query string."""
    if not url:
        return url
    parsed = urlparse(url)
    if not parsed.query:
        return url
    filtered = [
        (key, _REDACTED if key.lower() == "access_token" else value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
    ]
    if not filtered:
        return urlunparse(parsed._replace(query=""))
    return urlunparse(parsed._replace(query=urlencode(filtered)))


def redact_headers(headers: Optional[Mapping[str, Any]]) -> Dict[str, str]:
    """Return a copy of HTTP headers with Authorization redacted."""
    if not headers:
        return {}
    redacted: Dict[str, str] = {}
    for key, value in headers.items():
        if key.lower() == "authorization":
            redacted[key] = f"Bearer {_REDACTED}"
        else:
            redacted[key] = str(value)
    return redacted
