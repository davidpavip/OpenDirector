from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


class TaskStatus(StrEnum):
    NEW = "new"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    task_type: str
    title: str
    payload: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))
    status: TaskStatus = TaskStatus.NEW
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    error: str | None = None

    def start(self) -> None:
        self.status = TaskStatus.RUNNING

    def complete(self) -> None:
        self.status = TaskStatus.COMPLETED

    def fail(self, error: str) -> None:
        self.status = TaskStatus.FAILED
        self.error = error
