from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


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
    """Provider-neutral request for one visual planning sketch."""

    production_id: str
    scene_id: str
    scene_title: str
    shot: SketchShot
    output_directory: Path

    style_context: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SketchResult:
    """Visual artifact returned by a sketch provider."""

    shot_id: str
    provider_id: str
    product_path: Path

    media_type: str = "image/svg+xml"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.shot_id.strip():
            raise ValueError("SketchResult shot_id cannot be empty")

        if not self.provider_id.strip():
            raise ValueError("SketchResult provider_id cannot be empty")
