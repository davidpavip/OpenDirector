from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from opendirector.artifact import Artifact
from opendirector.production import ProductionSpecification


@dataclass(frozen=True)
class RefineRequest:
    """Create a keyframe from an existing image artifact."""

    source_artifact: Artifact
    production_specification: ProductionSpecification
    output_directory: Path
    creative_direction: str = ""
