"""Pydantic models for full Canvas discussion topics."""

from typing import Annotated, Optional

from pydantic import Field

from ..common.untrusted_content import UntrustedContentMixin
from .discussion_summary_model import DiscussionSummary


class DiscussionDetail(DiscussionSummary, UntrustedContentMixin):
    """Full discussion topic including the prompt HTML."""

    message: Annotated[
        Optional[str],
        Field(description="Discussion prompt or first post as HTML"),
    ] = None
    message_text: Annotated[
        Optional[str],
        Field(
            description=("Plain-text version of message (populated by get_discussion)"),
        ),
    ] = None
    user_name: Annotated[
        Optional[str],
        Field(description="Display name of the topic author"),
    ] = None
