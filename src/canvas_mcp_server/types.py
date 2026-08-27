"""Type definitions for Canvas API parameters and responses."""

from typing import Any, Dict, Union

APIHeaders = Dict[str, str]
APIError = Union[str, Dict[str, Any]]
