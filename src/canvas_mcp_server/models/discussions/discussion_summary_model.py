"""Pydantic models for Canvas discussion summaries."""

from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field


class DiscussionSummary(BaseModel):
    """Summary metadata for a Canvas discussion topic (REST API)."""

    model_config = ConfigDict(populate_by_name=True)

    discussion_id: Annotated[
        int,
        Field(alias="id", description="The numeric Canvas ID of the discussion"),
    ]
    title: Annotated[
        Optional[str],
        Field(description="The discussion title"),
    ] = None
    posted_at: Annotated[
        Optional[datetime],
        Field(description="When the topic was posted"),
    ] = None
    last_reply_at: Annotated[
        Optional[datetime],
        Field(description="When the last reply was posted"),
    ] = None
    require_initial_post: Annotated[
        Optional[bool],
        Field(
            description=("When true, the user must post before viewing other replies"),
        ),
    ] = None
    user_can_see_posts: Annotated[
        Optional[bool],
        Field(description="Whether posts are visible to the current user"),
    ] = None
    discussion_subentry_count: Annotated[
        Optional[int],
        Field(description="Number of replies in the topic"),
    ] = None
    read_state: Annotated[
        Optional[str],
        Field(description="read or unread for the current user"),
    ] = None
    unread_count: Annotated[
        Optional[int],
        Field(description="Unread reply count for the current user"),
    ] = None
    published: Annotated[
        Optional[bool],
        Field(description="Whether the topic is published"),
    ] = None
    locked: Annotated[
        Optional[bool],
        Field(description="Whether the topic is closed for comments"),
    ] = None
    locked_for_user: Annotated[
        Optional[bool],
        Field(description="Whether the topic is locked for the current user"),
    ] = None
    lock_explanation: Annotated[
        Optional[str],
        Field(description="Why the topic is locked, when applicable"),
    ] = None
    lock_at: Annotated[
        Optional[datetime],
        Field(description="When the topic locks, if scheduled"),
    ] = None
    discussion_type: Annotated[
        Optional[str],
        Field(description="threaded, side_comment, or not_threaded"),
    ] = None
    assignment_id: Annotated[
        Optional[int],
        Field(description="Linked assignment id for graded discussions"),
    ] = None
    html_url: Annotated[
        Optional[str],
        Field(description="Canvas web URL for the discussion"),
    ] = None
    pinned: Annotated[
        Optional[bool],
        Field(description="Whether the topic is pinned"),
    ] = None
    is_announcement: Annotated[
        Optional[bool],
        Field(description="Whether this topic is an announcement"),
    ] = None
    subscription_hold: Annotated[
        Optional[str],
        Field(
            description=("Why the user cannot subscribe, e.g. initial_post_required"),
        ),
    ] = None
