from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class Intent:
    """Immutable creative contract.

    Intent defines why a creative work exists.
    It is not a prompt. Prompts can be derived from intent.
    """

    audience: str = ""
    emotion: str = ""
    message: str = ""
    tone: str = ""
    style: str = ""
    success_definition: str = ""
    constraints: tuple[str, ...] = ()
    priorities: tuple[str, ...] = ()
    creator_notes: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))
    version: int = 1
    parent_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def evolve(self, **changes: Any) -> "Intent":
        """Create a new intent version while preserving lineage."""
        return replace(
            self,
            **changes,
            id=str(uuid4()),
            version=self.version + 1,
            parent_id=self.id,
            created_at=datetime.now(timezone.utc),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "version": self.version,
            "parent_id": self.parent_id,
            "audience": self.audience,
            "emotion": self.emotion,
            "message": self.message,
            "tone": self.tone,
            "style": self.style,
            "success_definition": self.success_definition,
            "constraints": list(self.constraints),
            "priorities": list(self.priorities),
            "creator_notes": self.creator_notes,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }
