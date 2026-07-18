from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4


class ProductType(str, Enum):
    """Creative product categories recognized by OpenDirector."""

    SKETCH = "sketch"
    IMAGE = "image"
    ANIMATION = "animation"
    VOICE = "voice"
    MUSIC = "music"
    AUDIO = "audio"
    EDIT = "edit"
    REVIEW = "review"
    SCENE = "scene"
    FINAL = "final"


@dataclass(frozen=True)
class CreativeProduct:
    """Provider-neutral creative output owned by a production.

    Ownership hierarchy:

        Production
            └── Scene, optional
                    └── Shot, optional

    Providers create products but never own them.
    """

    product_type: ProductType
    path: Path
    production_id: str

    id: str = field(default_factory=lambda: str(uuid4()))
    scene_id: str | None = None
    shot_id: str | None = None
    provider_id: str | None = None
    media_type: str = "application/octet-stream"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.production_id.strip():
            raise ValueError("CreativeProduct production_id cannot be empty")

        if self.scene_id is not None and not self.scene_id.strip():
            raise ValueError("CreativeProduct scene_id cannot be empty")

        if self.shot_id is not None and not self.shot_id.strip():
            raise ValueError("CreativeProduct shot_id cannot be empty")

        if self.shot_id is not None and self.scene_id is None:
            raise ValueError("A shot-owned product must also belong to a scene")

        if self.provider_id is not None and not self.provider_id.strip():
            raise ValueError("CreativeProduct provider_id cannot be empty")

    @property
    def filename(self) -> str:
        return self.path.name

    @property
    def exists(self) -> bool:
        return self.path.is_file()

    @property
    def scope(self) -> str:
        if self.shot_id is not None:
            return "shot"

        if self.scene_id is not None:
            return "scene"

        return "production"
