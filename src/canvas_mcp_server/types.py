"""Type definitions for Canvas API parameters and responses."""

from typing import Dict, Any, Union

APIHeaders = Dict[str, str]
APIError = Union[str, Dict[str, Any]]
