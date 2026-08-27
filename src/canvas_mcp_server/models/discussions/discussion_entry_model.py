"""Pydantic models for Canvas discussion entries."""

from typing import Annotated, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class DiscussionParticipant(BaseModel):
    """Author metadata from a discussion view response."""

    model_config = ConfigDict(populate_by_name=True)

    user_id: Annotated[
        int,
        Field(alias="id", description="Canvas user id"),
    ]
    display_name: Annotated[
        Optional[str],
        Field(description="Author display name"),
    ] = None


class DiscussionEntry(BaseModel):
    """One discussion post, with nested replies when threaded."""

    model_config = ConfigDict(populate_by_name=True)

    entry_id: Annotated[
        int,
        Field(alias="id", description="Canvas entry id"),
    ]
    user_id: Annotated[
        Optional[int],
        Field(description="Canvas user id of the author"),
    ] = None
    parent_id: Annotated[
        Optional[int],
        Field(description="Parent entry id for nested replies"),
    ] = None
    author_name: Annotated[
        Optional[str],
        Field(description="Resolved author display name"),
    ] = None
    message: Annotated[
        Optional[str],
        Field(description="Entry body as HTML"),
    ] = None
    message_text: Annotated[
        Optional[str],
        Field(
            description=(
                "Plain-text version of message (populated by get_discussion_entries)"
            ),
        ),
    ] = None
    replies: Annotated[
        List["DiscussionEntry"],
        Field(
            default_factory=list,
            description="Nested replies when Canvas returns a threaded view",
        ),
    ]


class DiscussionEntries(BaseModel):
    """Threaded discussion posts for one topic."""

    entries: Annotated[
        List[DiscussionEntry],
        Field(description="Top-level entries with nested replies"),
    ]
    unread_entry_ids: Annotated[
        List[int],
        Field(
            default_factory=list,
            description="Entry ids unread by the current user",
        ),
    ]
    participants: Annotated[
        List[DiscussionParticipant],
        Field(
            default_factory=list,
            description="Users who posted in the discussion",
        ),
    ]
    result_count: Annotated[
        int,
        Field(description="Number of top-level entries in entries"),
    ] = 0


DiscussionEntry.model_rebuild()
