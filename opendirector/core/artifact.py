from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


class ArtifactType(StrEnum):
    PROMPT = "prompt"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    SUBTITLE = "subtitle"
    REVIEW = "review"
    TIMELINE = "timeline"
    REPORT = "report"
    OTHER = "other"


@dataclass
class Artifact:
    artifact_type: ArtifactType
    title: str
    uri: str | None = None
    data: dict[str, Any] = field(default_factory=dict)
    created_by: str = "unknown"
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "artifact_type": self.artifact_type.value,
            "title": self.title,
            "uri": self.uri,
            "data": self.data,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
        }
