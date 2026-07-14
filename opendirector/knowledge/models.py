from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class KnowledgeKind(str, Enum):
    """The three layers of the Studio Mind."""

    VALUE = "value"
    EDUCATION = "education"
    EXPERIENCE = "experience"


class KnowledgeStatus(str, Enum):
    """Lifecycle state of a knowledge record."""

    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


@dataclass(frozen=True)
class KnowledgeEvidence:
    """Evidence supporting an education or experience record."""

    source: str
    description: str = ""
    reference_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class KnowledgeRecord:
    """One structured unit of Studio knowledge."""

    kind: KnowledgeKind
    title: str
    statement: str

    id: str = field(default_factory=lambda: str(uuid4()))
    status: KnowledgeStatus = KnowledgeStatus.PROPOSED

    scope: tuple[str, ...] = ()
    confidence: float = 1.0
    evidence: tuple[KnowledgeEvidence, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("Knowledge title cannot be empty")

        if not self.statement.strip():
            raise ValueError("Knowledge statement cannot be empty")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Knowledge confidence must be between 0 and 1")

        if self.kind is KnowledgeKind.VALUE and self.status is KnowledgeStatus.PROPOSED:
            # Values must be explicitly approved by the filmmaker before use.
            return

    @property
    def is_active(self) -> bool:
        return self.status is KnowledgeStatus.APPROVED

    @property
    def priority(self) -> int:
        """Higher priority knowledge governs lower priority knowledge."""

        priorities = {
            KnowledgeKind.VALUE: 300,
            KnowledgeKind.EDUCATION: 200,
            KnowledgeKind.EXPERIENCE: 100,
        }
        return priorities[self.kind]

    def applies_to(self, subject: str) -> bool:
        """Return whether this record applies to the requested subject."""

        if not self.scope:
            return True

        normalized = subject.strip().lower()
        return normalized in {item.strip().lower() for item in self.scope}
