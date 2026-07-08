from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from opendirector.core.timestamp import Timestamp, TimestampInput
from opendirector.core.track import Track


@dataclass
class TimelineEvent:
    """Base object for anything placed on the movie timeline."""

    start: Timestamp
    duration: Timestamp
    track: Track
    event_type: str
    id: str = field(default_factory=lambda: str(uuid4()))
    tags: set[str] = field(default_factory=set)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        *,
        start: TimestampInput,
        duration: TimestampInput,
        track: Track | str,
        event_type: str,
        tags: set[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "TimelineEvent":
        return cls(
            start=Timestamp.parse(start),
            duration=Timestamp.parse(duration),
            track=Track(track),
            event_type=event_type,
            tags=tags or set(),
            metadata=metadata or {},
        )

    @property
    def end(self) -> Timestamp:
        return self.start + self.duration

    def contains(self, timestamp: TimestampInput) -> bool:
        ts = Timestamp.parse(timestamp)
        return self.start <= ts < self.end

    def overlaps(self, other: "TimelineEvent") -> bool:
        return self.start < other.end and other.start < self.end

    def move_to(self, new_start: TimestampInput) -> None:
        self.start = Timestamp.parse(new_start)

    def add_tag(self, tag: str) -> None:
        self.tags.add(tag)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "start": str(self.start),
            "duration": str(self.duration),
            "end": str(self.end),
            "track": self.track.value,
            "event_type": self.event_type,
            "tags": sorted(self.tags),
            "metadata": self.metadata,
        }
