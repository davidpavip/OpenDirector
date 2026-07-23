from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from opendirector.animation.models import AnimationMode
from opendirector.artifact import Artifact
from opendirector.directing import ShotDirection
from opendirector.production import ProductionSpecification


@dataclass(frozen=True)
class AnimationRequest:
    """Provider-independent request to create or revise one clip."""

    production_id: str
    scene_id: str
    shot_id: str

    direction: ShotDirection
    production_specification: ProductionSpecification
    output_directory: Path

    mode: AnimationMode = AnimationMode.GENERATE

    keyframe: Artifact | None = None
    end_keyframe: Artifact | None = None
    driving_audio: Artifact | None = None
    source_clip: Artifact | None = None

    duration_seconds: float | None = None

    retake_start_seconds: float | None = None
    retake_duration_seconds: float | None = None

    def validate(self) -> None:
        if self.duration_seconds is not None:
            if self.duration_seconds <= 0:
                raise ValueError("Animation duration must be greater than zero")

        if self.mode is AnimationMode.GENERATE:
            self._validate_generate()
            return

        if self.mode is AnimationMode.AUDIO_DRIVEN:
            self._validate_audio_driven()
            return

        if self.mode is AnimationMode.RETAKE:
            self._validate_retake()
            return

        raise ValueError(f"Unsupported animation mode: {self.mode}")

    def _validate_generate(self) -> None:
        if self.source_clip is not None:
            raise ValueError("Generate mode cannot use a source clip")

        if self.driving_audio is not None:
            raise ValueError(
                "Generate mode cannot use driving audio; " "use audio-driven mode"
            )

    def _validate_audio_driven(self) -> None:
        if self.driving_audio is None:
            raise ValueError("Audio-driven animation requires driving audio")

        if not self.driving_audio.exists:
            raise FileNotFoundError(
                "Driving audio artifact does not exist: "
                f"{self.driving_audio.location}"
            )

        if self.source_clip is not None:
            raise ValueError("Audio-driven mode cannot use a source clip")

    def _validate_retake(self) -> None:
        if self.source_clip is None:
            raise ValueError("Retake mode requires a source clip")

        if not self.source_clip.exists:
            raise FileNotFoundError(
                "Source clip artifact does not exist: " f"{self.source_clip.location}"
            )

        if self.retake_start_seconds is None:
            raise ValueError("Retake mode requires retake_start_seconds")

        if self.retake_start_seconds < 0:
            raise ValueError("Retake start time cannot be negative")

        if self.retake_duration_seconds is None:
            raise ValueError("Retake mode requires retake_duration_seconds")

        if self.retake_duration_seconds <= 0:
            raise ValueError("Retake duration must be greater than zero")
