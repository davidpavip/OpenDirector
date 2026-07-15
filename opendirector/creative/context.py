from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from opendirector.core.candidate import CandidateSet
    from opendirector.core.intent import Intent
    from opendirector.core.movie import Movie
    from opendirector.core.scene import Scene
    from opendirector.planning.context import PlanningContext


@dataclass
class CreativeContext:
    """Shared working state for CreativePrograms."""

    intent: Intent | None = None
    movie: Movie | None = None
    scene: Scene | None = None
    candidate_set: CandidateSet | None = None

    # Temporary compatibility bridge.
    # Planning will eventually become a section of StudioContext.
    planning: PlanningContext | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    def record(self, key: str, value: Any) -> None:
        self.metadata[key] = value
