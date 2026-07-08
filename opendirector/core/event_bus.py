from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, DefaultDict
from collections import defaultdict


@dataclass(frozen=True)
class DomainEvent:
    """A fact that happened inside OpenDirector."""

    name: str
    payload: dict[str, Any] = field(default_factory=dict)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


EventHandler = Callable[[DomainEvent], None]


class EventBus:
    """Publish domain events to subscribed handlers."""

    def __init__(self) -> None:
        self._handlers: DefaultDict[str, list[EventHandler]] = defaultdict(list)
        self._wildcard_handlers: list[EventHandler] = []

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        self._handlers[event_name].append(handler)

    def subscribe_all(self, handler: EventHandler) -> None:
        self._wildcard_handlers.append(handler)

    def publish(self, event: DomainEvent) -> None:
        for handler in self._handlers.get(event.name, []):
            handler(event)
        for handler in self._wildcard_handlers:
            handler(event)
