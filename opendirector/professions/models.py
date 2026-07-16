from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class AssignmentStatus(str, Enum):
    PENDING = "pending"
    PREPARED = "prepared"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class Assignment:
    """One unit of professional work assigned by the Studio."""

    profession: str
    objective: str

    id: str = field(default_factory=lambda: str(uuid4()))
    production_id: str | None = None
    deliverable_type: str = ""
    constraints: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.profession.strip():
            raise ValueError("Assignment profession cannot be empty")

        if not self.objective.strip():
            raise ValueError("Assignment objective cannot be empty")


@dataclass(frozen=True)
class PreparedAssignment:
    """An assignment enriched with the Studio's current context."""

    assignment: Assignment

    values: tuple[str, ...] = ()
    education: tuple[str, ...] = ()
    experience: tuple[str, ...] = ()

    source_context: str = ""
    production_context: str = ""
    conversation_context: str = ""

    prepared_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def profession(self) -> str:
        return self.assignment.profession

    @property
    def objective(self) -> str:
        return self.assignment.objective


@dataclass(frozen=True)
class Deliverable:
    """Structured work returned by a profession."""

    assignment_id: str
    profession: str
    content: Any

    id: str = field(default_factory=lambda: str(uuid4()))
    deliverable_type: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.assignment_id.strip():
            raise ValueError("Deliverable assignment_id cannot be empty")

        if not self.profession.strip():
            raise ValueError("Deliverable profession cannot be empty")


@dataclass(frozen=True)
class Reflection:
    """A profession's evidence-based evaluation of completed work."""

    assignment_id: str
    profession: str
    summary: str

    id: str = field(default_factory=lambda: str(uuid4()))
    lessons: tuple[str, ...] = ()
    strengths: tuple[str, ...] = ()
    weaknesses: tuple[str, ...] = ()
    confidence: float = 0.5
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.assignment_id.strip():
            raise ValueError("Reflection assignment_id cannot be empty")

        if not self.profession.strip():
            raise ValueError("Reflection profession cannot be empty")

        if not self.summary.strip():
            raise ValueError("Reflection summary cannot be empty")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Reflection confidence must be between 0 and 1")


@dataclass(frozen=True)
class ProfessionResult:
    """Complete result of one professional invocation."""

    assignment: Assignment
    prepared: PreparedAssignment
    deliverable: Deliverable
    reflection: Reflection | None = None

    @property
    def completed(self) -> bool:
        return self.deliverable.assignment_id == self.assignment.id
