from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AnimationMode(StrEnum):
    """Provider-independent animation workflow."""

    GENERATE = "generate"
    AUDIO_DRIVEN = "audio_driven"
    RETAKE = "retake"


@dataclass(frozen=True)
class AnimationCapabilities:
    """Animation workflows supported by one provider."""

    text_to_video: bool = False
    image_to_video: bool = False
    audio_to_video: bool = False
    retake: bool = False
    first_last_frame: bool = False
    native_audio: bool = False

    def supports(
        self,
        mode: AnimationMode,
    ) -> bool:
        if mode is AnimationMode.GENERATE:
            return self.text_to_video or self.image_to_video

        if mode is AnimationMode.AUDIO_DRIVEN:
            return self.audio_to_video

        if mode is AnimationMode.RETAKE:
            return self.retake

        return False
