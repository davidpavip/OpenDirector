from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from opendirector.professions import Assignment, ProfessionContext
from opendirector.thinking.models import Understanding


@dataclass
class ThinkingContext:
    """Temporary working state for a profession's thinking program.

    This will eventually become a section of StudioContext.
    """

    assignment: Assignment
    profession_context: ProfessionContext

    understanding: Understanding | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def record(self, key: str, value: Any) -> None:
        self.metadata[key] = value
