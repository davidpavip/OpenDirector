"""Core event primitives for OpenDirector.

OpenDirector principle:

    Everything is a Timeline Event.

But before timeline events, we need a smaller primitive:

    DomainEvent

A DomainEvent is a fact that happened inside OpenDirector.
Some DomainEvents live on the timeline. Others do not.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import uuid4


@dataclass(frozen=True)
class EventId:
    """Stable identifier for an event."""

    value: str = field(default_factory=lambda: str(uuid4()))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class DomainEvent:
    """A fact that happened inside OpenDirector.

    Examples:
        - project.opened
        - project.saved
        - render.started
        - render.finished
        - timeline.event_added

    DomainEvent is intentionally small and immutable.
    It should be easy to serialize, log, test, and pass between modules.
    """

    name: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    id: EventId = field(default_factory=EventId)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "opendirector"

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("DomainEvent.name cannot be empty")

        if self.occurred_at.tzinfo is None:
            raise ValueError("DomainEvent.occurred_at must be timezone-aware")

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly dictionary."""

        return {
            "id": str(self.id),
            "name": self.name,
            "payload": dict(self.payload),
            "occurred_at": self.occurred_at.isoformat(),
            "source": self.source,
        }
