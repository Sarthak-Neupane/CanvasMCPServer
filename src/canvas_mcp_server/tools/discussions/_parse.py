"""Helpers for Canvas discussion REST responses."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ...models import DiscussionEntries, DiscussionEntry, DiscussionParticipant
from ...utils.content_metadata import attach_content_metadata
from ...utils.html import html_to_text


def _participant_map(
    participants: List[Dict[str, Any]],
) -> Dict[int, str]:
    names: Dict[int, str] = {}
    for participant in participants:
        if not isinstance(participant, dict):
            continue
        user_id = participant.get("id")
        display_name = participant.get("display_name")
        if user_id is not None and display_name:
            names[int(user_id)] = str(display_name)
    return names


def _entry_from_view(
    raw: Dict[str, Any],
    *,
    names: Dict[int, str],
    course_id: str,
    discussion_id: str,
) -> DiscussionEntry:
    user_id = raw.get("user_id")
    author_name = names.get(int(user_id)) if user_id is not None else None
    message = raw.get("message")
    replies_raw = raw.get("replies") or []
    replies = [
        _entry_from_view(
            reply,
            names=names,
            course_id=course_id,
            discussion_id=discussion_id,
        )
        for reply in replies_raw
        if isinstance(reply, dict)
    ]
    entry = DiscussionEntry.model_validate(
        {
            **raw,
            "author_name": author_name,
            "replies": [],
        }
    )
    message_text = html_to_text(message) if message else None
    entry = entry.model_copy(
        update={
            "message_text": message_text,
            "replies": replies,
        }
    )
    return attach_content_metadata(
        entry,
        source_type="discussion_entry",
        course_id=course_id,
        resource_id=str(entry.entry_id),
        canvas_url=f"/courses/{course_id}/discussion_topics/{discussion_id}/entries/{entry.entry_id}",
    )


def discussion_entries_from_view(
    raw: Dict[str, Any],
    *,
    course_id: str,
    discussion_id: str,
) -> DiscussionEntries:
    """Convert a Canvas discussion view payload to DiscussionEntries."""
    participants_raw = raw.get("participants") or []
    participants = [
        DiscussionParticipant.model_validate(participant)
        for participant in participants_raw
        if isinstance(participant, dict)
    ]
    names = _participant_map(participants_raw)
    view = raw.get("view") or []
    entries = [
        _entry_from_view(
            entry,
            names=names,
            course_id=course_id,
            discussion_id=discussion_id,
        )
        for entry in view
        if isinstance(entry, dict)
    ]
    unread = raw.get("unread_entries") or []
    unread_ids = [int(entry_id) for entry_id in unread if entry_id is not None]
    return DiscussionEntries(
        entries=entries,
        unread_entry_ids=unread_ids,
        participants=participants,
        result_count=len(entries),
    )
