from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from opendirector.core.candidate import CandidateSet
from opendirector.core.intent import Intent
from opendirector.core.movie import Movie
from opendirector.core.scene import Scene


@dataclass
class CreativeContext:
    """Shared state passed through a CreativeProgram."""

    intent: Intent | None = None
    movie: Movie | None = None
    scene: Scene | None = None
    candidate_set: CandidateSet | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def record(self, key: str, value: Any) -> None:
        self.metadata[key] = value
