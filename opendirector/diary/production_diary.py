from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from opendirector.core.event_bus import DomainEvent, EventBus


@dataclass
class DiaryEntry:
    """A human-readable record of something that happened during production."""

    timestamp: datetime
    title: str
    body: str

    def to_markdown(self) -> str:
        ts = self.timestamp.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        return f"## {self.title}\n\n_Time: {ts}_\n\n{self.body}\n"


class ProductionDiary:
    """Record important creative and technical events for a project."""

    def __init__(self, project_path: str | Path) -> None:
        self.project_path = Path(project_path)
        self.diary_dir = self.project_path / "diary"
        self.diary_dir.mkdir(parents=True, exist_ok=True)
        self.entries: list[DiaryEntry] = []

    def connect(self, event_bus: EventBus) -> None:
        event_bus.subscribe("timeline.event_added", self.on_timeline_event_added)
        event_bus.subscribe_all(self.on_any_event)

    def on_timeline_event_added(self, event: DomainEvent) -> None:
        payload = event.payload
        event_type = payload.get("event_type", "unknown")
        track = payload.get("track", "unknown")
        start = payload.get("start", 0)
        duration = payload.get("duration", 0)
        metadata = payload.get("metadata", {})

        title = f"Timeline event added: {event_type}"
        body = (
            f"- Track: `{track}`\n"
            f"- Start: `{start:.2f}s`\n"
            f"- Duration: `{duration:.2f}s`\n"
            f"- Metadata: `{metadata}`"
        )
        self.entries.append(DiaryEntry(event.occurred_at, title, body))

    def on_any_event(self, event: DomainEvent) -> None:
        if event.name == "timeline.event_added":
            return
        self.entries.append(
            DiaryEntry(
                event.occurred_at,
                f"Domain event: {event.name}",
                f"Payload: `{event.payload}`",
            )
        )

    def write(self) -> Path:
        output = self.diary_dir / "production_diary.md"
        header = (
            "# Production Diary\n\n"
            "This file is generated from OpenDirector domain events.\n\n"
        )
        text = header + "\n".join(entry.to_markdown() for entry in self.entries)
        output.write_text(text, encoding="utf-8")
        return output
