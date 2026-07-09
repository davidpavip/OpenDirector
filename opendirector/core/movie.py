from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from opendirector.core.candidate import CandidateSet
from opendirector.core.scene import Scene
from opendirector.core.intent import Intent


@dataclass
class Movie:
    """Creative container owned by a Studio."""

    title: str
    description: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    candidate_sets: list[CandidateSet] = field(default_factory=list)
    scenes: list[Scene] = field(default_factory=list)
    intent: Intent | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("Movie title cannot be empty")

    def add_candidate_set(self, candidate_set: CandidateSet) -> CandidateSet:
        self.candidate_sets.append(candidate_set)
        return candidate_set

    def create_scene(
        self,
        title: str,
        summary: str = "",
        goal: str = "",
        sequence: int | None = None,
    ) -> Scene:
        if sequence is None:
            sequence = len(self.scenes) + 1

        scene = Scene(
            title=title,
            summary=summary,
            goal=goal,
            sequence=sequence,
        )
        self.scenes.append(scene)
        self.scenes.sort(key=lambda s: s.sequence)
        return scene

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "candidate_sets": [
                {
                    "id": cs.id,
                    "purpose": cs.purpose,
                    "candidate_count": len(cs.candidates),
                    "selected_id": cs.selected_id,
                }
                for cs in self.candidate_sets
            ],
            "scenes": [scene.to_dict() for scene in self.scenes],
            "metadata": self.metadata,
        }
