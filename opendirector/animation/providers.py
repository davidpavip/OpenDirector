from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from opendirector.animation.clip import GeneratedClip
from opendirector.animation.models import (
    AnimationCapabilities,
    AnimationMode,
)
from opendirector.animation.request import (
    AnimationRequest,
)
from opendirector.artifact import Artifact, Kind


class AnimationProvider(ABC):
    """Provider capable of generating or revising one clip."""

    provider_id: str
    capabilities: AnimationCapabilities

    @abstractmethod
    async def animate(
        self,
        request: AnimationRequest,
    ) -> GeneratedClip:
        raise NotImplementedError

    def validate_request(
        self,
        request: AnimationRequest,
    ) -> None:
        request.validate()

        if not self.capabilities.supports(request.mode):
            raise ValueError(
                f"Provider {self.provider_id!r} does not "
                f"support mode {request.mode.value!r}"
            )


class MockAnimationProvider(AnimationProvider):
    """Deterministic LTX-shaped provider for tests."""

    provider_id = "mock.animation"

    capabilities = AnimationCapabilities(
        text_to_video=True,
        image_to_video=True,
        audio_to_video=True,
        retake=True,
        first_last_frame=True,
        native_audio=True,
    )

    async def animate(
        self,
        request: AnimationRequest,
    ) -> GeneratedClip:
        self.validate_request(request)

        request.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        duration = self._resolve_duration(request)

        output_path = self._next_output_path(
            output_directory=request.output_directory,
            shot_id=request.shot_id,
            mode=request.mode,
        )

        output_path.write_bytes(
            self._placeholder_payload(
                request=request,
                duration_seconds=duration,
            )
        )

        source_keyframe_id = (
            request.keyframe.id if request.keyframe is not None else None
        )

        end_keyframe_id = (
            request.end_keyframe.id if request.end_keyframe is not None else None
        )

        driving_audio_id = (
            request.driving_audio.id if request.driving_audio is not None else None
        )

        source_clip_id = (
            request.source_clip.id if request.source_clip is not None else None
        )

        has_audio = self.capabilities.native_audio or request.driving_audio is not None

        artifact = Artifact(
            production_id=request.production_id,
            scene_id=request.scene_id,
            shot_id=request.shot_id,
            kind=Kind.VIDEO,
            location=output_path,
            media_type="video/mp4",
            metadata={
                "role": "clip",
                "provider_id": self.provider_id,
                "animation_mode": request.mode.value,
                "source_keyframe_id": (source_keyframe_id),
                "end_keyframe_id": end_keyframe_id,
                "driving_audio_id": driving_audio_id,
                "source_clip_id": source_clip_id,
                "duration_seconds": duration,
                "orientation": (request.production_specification.preferred_orientation),
                "aspect_ratio": (request.production_specification.aspect_ratio),
                "has_audio": has_audio,
                "audio_baked_in": has_audio,
            },
        )

        return GeneratedClip(
            artifact=artifact,
            duration_seconds=duration,
            mode=request.mode,
            provider_id=self.provider_id,
            has_video=True,
            has_audio=has_audio,
            audio_baked_in=has_audio,
            metadata={
                "direction_shot_id": (request.direction.shot_id),
                "reference_audio_used": (request.driving_audio is not None),
                "retake_start_seconds": (request.retake_start_seconds),
                "retake_duration_seconds": (request.retake_duration_seconds),
            },
        )

    @staticmethod
    def _resolve_duration(
        request: AnimationRequest,
    ) -> float:
        if request.mode is AnimationMode.RETAKE:
            assert request.retake_duration_seconds is not None
            return request.retake_duration_seconds

        if request.duration_seconds is not None:
            return request.duration_seconds

        metadata_duration = request.direction.metadata.get("duration_seconds")

        if isinstance(
            metadata_duration,
            int | float,
        ):
            if metadata_duration > 0:
                return float(metadata_duration)

        return 5.0

    @staticmethod
    def _next_output_path(
        output_directory: Path,
        shot_id: str,
        mode: AnimationMode,
    ) -> Path:
        iteration = 1

        while True:
            candidate = output_directory / (
                f"{shot_id}-{mode.value}-" f"{iteration:03d}.mp4"
            )

            if not candidate.exists():
                return candidate

            iteration += 1

    def _placeholder_payload(
        self,
        request: AnimationRequest,
        duration_seconds: float,
    ) -> bytes:
        lines = [
            "OpenDirector Mock Clip",
            f"provider={self.provider_id}",
            f"mode={request.mode.value}",
            f"production={request.production_id}",
            f"scene={request.scene_id}",
            f"shot={request.shot_id}",
            f"duration={duration_seconds:g}",
            (
                "keyframe=" f"{request.keyframe.location}"
                if request.keyframe is not None
                else "keyframe="
            ),
            (
                "driving_audio=" f"{request.driving_audio.location}"
                if request.driving_audio is not None
                else "driving_audio="
            ),
            (
                "source_clip=" f"{request.source_clip.location}"
                if request.source_clip is not None
                else "source_clip="
            ),
            "",
        ]

        return "\n".join(lines).encode("utf-8")
