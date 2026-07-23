from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from opendirector.animation.models import AnimationMode
from opendirector.artifact import Artifact, Kind


@dataclass(frozen=True)
class GeneratedClip:
    """One provider-generated audiovisual shot result."""

    artifact: Artifact
    duration_seconds: float
    mode: AnimationMode
    provider_id: str

    has_video: bool = True
    has_audio: bool = False
    audio_baked_in: bool = False

    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.artifact.kind is not Kind.VIDEO:
            raise ValueError("GeneratedClip requires a video Artifact")

        if self.duration_seconds <= 0:
            raise ValueError("Clip duration must be greater than zero")

        if self.audio_baked_in and not self.has_audio:
            raise ValueError("Baked audio requires has_audio=True")
