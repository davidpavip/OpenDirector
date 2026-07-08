from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Literal, Optional
import json

EventKind = Literal[
    "story_beat",
    "video_clip",
    "audio",
    "music",
    "sound_effect",
    "subtitle",
    "camera",
    "transition",
    "review",
    "director_note",
]


@dataclass(order=True)
class TimelineEvent:
    """A creative event that happens on the movie timeline."""

    start: float
    duration: float
    kind: EventKind
    id: str
    track: str
    label: str = ""
    asset: Optional[str] = None
    intent: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def end(self) -> float:
        return self.start + self.duration

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["end"] = self.end
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TimelineEvent":
        clean = dict(data)
        clean.pop("end", None)
        return cls(**clean)


@dataclass
class Timeline:
    """The shared creative timeline of a movie."""

    id: str = "main"
    fps: int = 24
    events: List[TimelineEvent] = field(default_factory=list)

    def add(self, event: TimelineEvent) -> TimelineEvent:
        if event.duration < 0:
            raise ValueError("TimelineEvent duration must be non-negative")
        self.events.append(event)
        self.events.sort(key=lambda e: (e.start, e.track, e.id))
        return event

    def add_clip(
        self,
        *,
        id: str,
        asset: str,
        start: float,
        duration: float,
        label: str = "",
        intent: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TimelineEvent:
        return self.add(
            TimelineEvent(
                id=id,
                kind="video_clip",
                track="video",
                start=start,
                duration=duration,
                asset=asset,
                label=label,
                intent=intent,
                metadata=metadata or {},
            )
        )

    def add_story_beat(
        self,
        *,
        id: str,
        start: float,
        duration: float,
        label: str,
        intent: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TimelineEvent:
        return self.add(
            TimelineEvent(
                id=id,
                kind="story_beat",
                track="story",
                start=start,
                duration=duration,
                label=label,
                intent=intent,
                metadata=metadata or {},
            )
        )

    def add_transition(
        self,
        *,
        id: str,
        start: float,
        duration: float,
        label: str = "crossfade",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TimelineEvent:
        return self.add(
            TimelineEvent(
                id=id,
                kind="transition",
                track="transition",
                start=start,
                duration=duration,
                label=label,
                metadata=metadata or {},
            )
        )

    def by_track(self, track: str) -> List[TimelineEvent]:
        return [e for e in self.events if e.track == track]

    def by_kind(self, kind: EventKind) -> List[TimelineEvent]:
        return [e for e in self.events if e.kind == kind]

    @property
    def duration(self) -> float:
        return max((e.end for e in self.events), default=0.0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "fps": self.fps,
            "duration": self.duration,
            "events": [e.to_dict() for e in self.events],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Timeline":
        timeline = cls(id=data.get("id", "main"), fps=int(data.get("fps", 24)))
        for item in data.get("events", []):
            timeline.add(TimelineEvent.from_dict(item))
        return timeline

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "Timeline":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


def timeline_from_shots(shots: Iterable[Any], *, fps: int = 24, crossfade: float = 0.0) -> Timeline:
    """Create a first-cut timeline from ordered Shot objects."""
    timeline = Timeline(id="director_cut_v1", fps=fps)
    cursor = 0.0
    previous_end = 0.0

    for index, shot in enumerate(shots, start=1):
        start = max(0.0, cursor)
        timeline.add_story_beat(
            id=f"beat_{shot.id}",
            start=start,
            duration=float(shot.duration),
            label=f"{shot.id} intent",
            intent=shot.video_prompt,
            metadata={"scene_id": shot.scene_id, "camera": shot.camera, "motion": shot.motion},
        )
        timeline.add_clip(
            id=shot.id,
            asset=shot.video_file,
            start=start,
            duration=float(shot.duration),
            label=shot.id,
            intent=shot.video_prompt,
            metadata={"scene_id": shot.scene_id, "image_file": shot.image_file},
        )
        if index > 1 and crossfade > 0:
            timeline.add_transition(
                id=f"transition_{index-1:03d}_{index:03d}",
                start=max(0.0, start),
                duration=float(crossfade),
                label="crossfade",
                metadata={"from_previous": True},
            )
        previous_end = start + float(shot.duration)
        cursor = previous_end - float(crossfade)

    return timeline
