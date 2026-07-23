from __future__ import annotations

from typing import Any, Iterable

from opendirector.core.event_bus import (
    DomainEvent,
    EventBus,
)

from opendirector.core.timeline_event import (
    TimelineEvent,
)
from opendirector.core.timestamp import (
    Timestamp,
    TimestampInput,
)
from opendirector.core.track import Track


class StoryBeatEvent(TimelineEvent):
    """A story-intent event used to guide other operators."""

    def __init__(
        self,
        start: TimestampInput,
        duration: TimestampInput,
        goal: str,
        emotion: str = "",
        importance: str = "normal",
    ) -> None:
        super().__init__(
            start=Timestamp.parse(start),
            duration=Timestamp.parse(duration),
            track=Track.STORY,
            event_type="story_beat",
            metadata={
                "goal": goal,
                "emotion": emotion,
                "importance": importance,
            },
        )


class VideoClipEvent(TimelineEvent):
    """A rendered or imported clip placed on a timeline."""

    def __init__(
        self,
        start: TimestampInput,
        duration: TimestampInput,
        clip_path: str,
        shot_id: str = "",
        trim_start: TimestampInput = 0,
    ) -> None:
        trim_timestamp = Timestamp.parse(trim_start)

        super().__init__(
            start=Timestamp.parse(start),
            duration=Timestamp.parse(duration),
            track=Track.VIDEO,
            event_type="video_clip",
            metadata={
                "clip_path": clip_path,
                "shot_id": shot_id,
                "trim_start_milliseconds": (trim_timestamp.milliseconds),
                "trim_start_seconds": (trim_timestamp.seconds),
            },
        )


class ReviewEvent(TimelineEvent):
    """A review comment or score attached to a time range."""

    def __init__(
        self,
        start: TimestampInput,
        duration: TimestampInput,
        score: int,
        comment: str,
        target_event_id: str = "",
    ) -> None:
        super().__init__(
            start=Timestamp.parse(start),
            duration=Timestamp.parse(duration),
            track=Track.REVIEW,
            event_type="review",
            metadata={
                "score": score,
                "comment": comment,
                "target_event_id": target_event_id,
            },
        )


class Timeline:
    """Creative events stored with exact millisecond timing."""

    def __init__(
        self,
        event_bus: EventBus | None = None,
    ) -> None:
        self.event_bus = event_bus or EventBus()
        self._events: list[TimelineEvent] = []

    def add(
        self,
        event: TimelineEvent,
    ) -> TimelineEvent:
        if event.duration.milliseconds < 0:
            raise ValueError("Timeline event duration cannot be negative")

        self._events.append(event)

        self._events.sort(
            key=lambda item: (
                item.start.milliseconds,
                item.track.value,
                item.event_type,
            )
        )

        self.event_bus.publish(
            DomainEvent(
                name="timeline.event_added",
                payload={
                    "event_id": event.id,
                    "event_type": event.event_type,
                    "track": event.track.value,
                    "start_milliseconds": (event.start.milliseconds),
                    "duration_milliseconds": (event.duration.milliseconds),
                    "end_milliseconds": (event.end.milliseconds),
                    "start_seconds": (event.start.seconds),
                    "duration_seconds": (event.duration.seconds),
                    "start_timestamp": str(event.start),
                    "duration_timestamp": str(event.duration),
                    "metadata": event.metadata,
                },
            )
        )

        return event

    def extend(
        self,
        events: Iterable[TimelineEvent],
    ) -> None:
        for event in events:
            self.add(event)

    def events(self) -> list[TimelineEvent]:
        return list(self._events)

    def by_track(
        self,
        track: Track | str,
    ) -> list[TimelineEvent]:
        resolved = Track(track)

        return [event for event in self._events if event.track is resolved]

    def find(
        self,
        **metadata_filters: Any,
    ) -> list[TimelineEvent]:
        return [
            event
            for event in self._events
            if all(
                event.metadata.get(key) == value
                for key, value in metadata_filters.items()
            )
        ]

    @property
    def duration_timestamp(self) -> Timestamp:
        if not self._events:
            return Timestamp.zero()

        return max(event.end for event in self._events)

    @property
    def duration_milliseconds(self) -> int:
        return self.duration_timestamp.milliseconds

    @property
    def duration_seconds(self) -> float:
        return self.duration_timestamp.seconds

    @property
    def duration(self) -> float:
        """Backward-compatible duration in seconds."""

        return self.duration_seconds
