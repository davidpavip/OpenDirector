from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4


class Kind(str, Enum):
    """Fundamental kinds of creative artifacts."""

    DOCUMENT = "document"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    SUBTITLE = "subtitle"
    COMPOSITE = "composite"
    TEXT = "text"


@dataclass(frozen=True)
class Artifact:
    """Persistent creative material owned by a production.

    Everything OpenDirector consumes or produces can be represented
    as an Artifact.
    """

    production_id: str
    kind: Kind
    location: Path

    id: str = field(default_factory=lambda: str(uuid4()))
    scene_id: str | None = None
    shot_id: str | None = None
    media_type: str = "application/octet-stream"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        production_id = self.production_id.strip()

        if not production_id:
            raise ValueError("Artifact production_id cannot be empty")

        if self.scene_id is not None:
            scene_id = self.scene_id.strip()

            if not scene_id:
                raise ValueError("Artifact scene_id cannot be empty")

        if self.shot_id is not None:
            shot_id = self.shot_id.strip()

            if not shot_id:
                raise ValueError("Artifact shot_id cannot be empty")

            if self.scene_id is None:
                raise ValueError("A shot artifact must also belong to a scene")

        if not isinstance(self.location, Path):
            raise TypeError("Artifact location must be a pathlib.Path")

        if not self.media_type.strip():
            raise ValueError("Artifact media_type cannot be empty")

    @property
    def filename(self) -> str:
        return self.location.name

    @property
    def exists(self) -> bool:
        return self.location.exists()

    @property
    def scope(self) -> str:
        if self.shot_id is not None:
            return "shot"

        if self.scene_id is not None:
            return "scene"

        return "production"
