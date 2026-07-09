from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable
from uuid import uuid4

from .event_bus import DomainEvent, EventBus


@dataclass
class TimelineEvent:
    """Base class for every creative event on the timeline."""

    start: float
    duration: float
    track: str
    event_type: str
    id: str = field(default_factory=lambda: str(uuid4()))
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def end(self) -> float:
        return self.start + self.duration


@dataclass
class StoryBeatEvent(TimelineEvent):
    """A story-intent event used to guide other agents."""

    def __init__(
        self,
        start: float,
        duration: float,
        goal: str,
        emotion: str = "",
        importance: str = "normal",
    ):
        super().__init__(
            start=start,
            duration=duration,
            track="story",
            event_type="story_beat",
            metadata={"goal": goal, "emotion": emotion, "importance": importance},
        )


@dataclass
class VideoClipEvent(TimelineEvent):
    """A rendered or imported video clip placed on the timeline."""

    def __init__(
        self,
        start: float,
        duration: float,
        clip_path: str,
        shot_id: str = "",
        trim_start: float = 0.0,
    ):
        super().__init__(
            start=start,
            duration=duration,
            track="video",
            event_type="video_clip",
            metadata={
                "clip_path": clip_path,
                "shot_id": shot_id,
                "trim_start": trim_start,
            },
        )


@dataclass
class ReviewEvent(TimelineEvent):
    """A review comment or score attached to a time range."""

    def __init__(
        self,
        start: float,
        duration: float,
        score: int,
        comment: str,
        target_event_id: str = "",
    ):
        super().__init__(
            start=start,
            duration=duration,
            track="review",
            event_type="review",
            metadata={
                "score": score,
                "comment": comment,
                "target_event_id": target_event_id,
            },
        )


class Timeline:
    """A movie represented as creative events over time."""

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self.event_bus = event_bus or EventBus()
        self._events: list[TimelineEvent] = []

    def add(self, event: TimelineEvent) -> TimelineEvent:
        self._events.append(event)
        self._events.sort(key=lambda e: (e.start, e.track, e.event_type))
        self.event_bus.publish(
            DomainEvent(
                name="timeline.event_added",
                payload={
                    "event_id": event.id,
                    "event_type": event.event_type,
                    "track": event.track,
                    "start": event.start,
                    "duration": event.duration,
                    "metadata": event.metadata,
                },
            )
        )
        return event

    def events(self) -> list[TimelineEvent]:
        return list(self._events)

    def by_track(self, track: str) -> list[TimelineEvent]:
        return [event for event in self._events if event.track == track]

    def find(self, **metadata_filters: Any) -> list[TimelineEvent]:
        results = []
        for event in self._events:
            if all(event.metadata.get(k) == v for k, v in metadata_filters.items()):
                results.append(event)
        return results

    @property
    def duration(self) -> float:
        if not self._events:
            return 0.0
        return max(event.end for event in self._events)
