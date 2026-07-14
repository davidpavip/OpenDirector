from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from opendirector.planning.models import ProductionBlueprint, SourceDocument


@dataclass
class PlanningContext:
    """Working context used while preparing a ProductionBlueprint."""

    source: SourceDocument
    blueprint: ProductionBlueprint | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.blueprint is None:
            self.blueprint = ProductionBlueprint(source=self.source)

    def record(self, key: str, value: Any) -> None:
        self.metadata[key] = value
