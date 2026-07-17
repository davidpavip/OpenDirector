from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from opendirector.planning import ScenePlanning
from opendirector.thinking import Understanding


@dataclass
class SceneThinkingContext:
    """Working state for planning one scene."""

    scene_id: str
    title: str

    production_understanding: Understanding | None = None
    scene: ScenePlanning | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    def record(self, key: str, value: Any) -> None:
        self.metadata[key] = value
