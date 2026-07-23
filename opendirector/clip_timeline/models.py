from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from opendirector.core.timestamp import Timestamp
from opendirector.artifact import Artifact, Kind
from opendirector.core.timeline import (
    Timeline,
    TimelineEvent,
)


@dataclass
class ClipTimeline:
    """Post-production timeline belonging to one generated clip."""

    production_id: str
    scene_id: str
    shot_id: str

    source_clip: Artifact
    duration_seconds: float

    status: str = "draft"
    metadata: dict[str, Any] = field(default_factory=dict)
    timeline: Timeline = field(default_factory=Timeline)

    def __post_init__(self) -> None:
        if self.source_clip.kind is not Kind.VIDEO:
            raise ValueError("ClipTimeline requires a video source artifact")

        if self.duration_seconds <= 0:
            raise ValueError("ClipTimeline duration must be greater than zero")

    @property
    def duration_timestamp(self) -> Timestamp:
        return Timestamp.from_seconds(self.duration_seconds)

    def add_event(
        self,
        event: TimelineEvent,
    ) -> TimelineEvent:
        if event.start.milliseconds < 0:
            raise ValueError(
                "Timeline event start cannot be negative"
            )

        if event.duration.milliseconds < 0:
            raise ValueError(
                "Timeline event duration cannot be negative"
            )

        if (
            event.end.milliseconds
            > self.duration_timestamp.milliseconds
        ):
            raise ValueError(
                "Timeline event exceeds clip duration"
            )

        return self.timeline.add(event)

    def events(
        self,
    ) -> list[TimelineEvent]:
        return self.timeline.events()

    def by_track(
        self,
        track: str,
    ) -> list[TimelineEvent]:
        return self.timeline.by_track(track)
