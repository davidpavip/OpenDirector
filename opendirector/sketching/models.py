from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from opendirector.production import ProductionSpecification

@dataclass(frozen=True)
class SketchShot:
    """Filmmaker-editable shot intent loaded from shots.md."""

    shot_id: str
    purpose: str
    camera: str
    duration_seconds: float
    intended_output: str = ""
    continuity: str = ""
    creative_notes: str = ""
    filmmaker_revision: str = ""

    def __post_init__(self) -> None:
        if not self.shot_id.strip():
            raise ValueError("SketchShot shot_id cannot be empty")

        if not self.purpose.strip():
            raise ValueError("SketchShot purpose cannot be empty")

        if self.duration_seconds <= 0:
            raise ValueError("SketchShot duration_seconds must be greater than zero")


@dataclass(frozen=True)
class SketchRequest:
    """Provider-neutral request for one visual sketch artifact."""

    production_id: str
    scene_id: str
    scene_title: str
    shot: SketchShot
    output_directory: Path

    production_specification: ProductionSpecification = field(
        default_factory=ProductionSpecification
    )

    style_context: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)