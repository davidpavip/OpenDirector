from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class Understanding:
    """Explicit understanding produced before creative work begins.

    Understanding answers:

    - What is the filmmaker asking for?
    - What goals must be achieved?
    - What constraints must be respected?
    - What assumptions are being made?
    - What remains unknown?
    - What risks may affect the work?
    """

    intent: str

    id: str = field(default_factory=lambda: str(uuid4()))
    goals: tuple[str, ...] = ()
    audience: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    unknowns: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()

    confidence: float = 0.5
    metadata: dict[str, Any] = field(default_factory=dict)

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.intent.strip():
            raise ValueError("Understanding intent cannot be empty")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Understanding confidence must be between 0 and 1")

    def is_ready(self, threshold: float = 0.7) -> bool:
        """Return whether understanding is sufficient to continue."""

        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Understanding threshold must be between 0 and 1")

        return self.confidence >= threshold and not self.unknowns

    def requires_clarification(
        self,
        threshold: float = 0.7,
    ) -> bool:
        return not self.is_ready(threshold)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "intent": self.intent,
            "goals": list(self.goals),
            "audience": list(self.audience),
            "constraints": list(self.constraints),
            "assumptions": list(self.assumptions),
            "unknowns": list(self.unknowns),
            "risks": list(self.risks),
            "evidence": list(self.evidence),
            "confidence": self.confidence,
            "metadata": dict(self.metadata),
            "created_at": self.created_at.isoformat(),
        }
