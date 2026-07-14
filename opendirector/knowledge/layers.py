from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from opendirector.knowledge.models import (
    KnowledgeEvidence,
    KnowledgeKind,
    KnowledgeRecord,
    KnowledgeStatus,
)


@dataclass(frozen=True)
class Value:
    """A filmmaker-approved principle governing Studio decisions."""

    title: str
    statement: str
    scope: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_record(self) -> KnowledgeRecord:
        return KnowledgeRecord(
            kind=KnowledgeKind.VALUE,
            title=self.title,
            statement=self.statement,
            status=KnowledgeStatus.APPROVED,
            scope=self.scope,
            confidence=1.0,
            metadata=dict(self.metadata),
        )


@dataclass(frozen=True)
class Education:
    """Professional knowledge learned from external sources."""

    title: str
    statement: str
    source: str

    scope: tuple[str, ...] = ()
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_record(self) -> KnowledgeRecord:
        return KnowledgeRecord(
            kind=KnowledgeKind.EDUCATION,
            title=self.title,
            statement=self.statement,
            status=KnowledgeStatus.APPROVED,
            scope=self.scope,
            confidence=self.confidence,
            evidence=(
                KnowledgeEvidence(
                    source=self.source,
                    description="External professional education",
                ),
            ),
            metadata=dict(self.metadata),
        )


@dataclass(frozen=True)
class Experience:
    """Knowledge learned through Studio production activity."""

    title: str
    statement: str
    production_id: str

    scope: tuple[str, ...] = ()
    confidence: float = 0.5
    evidence_description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_record(self) -> KnowledgeRecord:
        return KnowledgeRecord(
            kind=KnowledgeKind.EXPERIENCE,
            title=self.title,
            statement=self.statement,
            status=KnowledgeStatus.APPROVED,
            scope=self.scope,
            confidence=self.confidence,
            evidence=(
                KnowledgeEvidence(
                    source="production",
                    reference_id=self.production_id,
                    description=self.evidence_description,
                ),
            ),
            metadata=dict(self.metadata),
        )
