from __future__ import annotations

import base64
from dataclasses import dataclass
import mimetypes
import os
from pathlib import Path
from typing import Any

import requests

from opendirector.animation.clip import GeneratedClip
from opendirector.animation.ltx_prompt import (
    LTXPromptBuilder,
)
from opendirector.animation.models import (
    AnimationCapabilities,
    AnimationMode,
)
from opendirector.animation.providers import (
    AnimationProvider,
)
from opendirector.animation.request import (
    AnimationRequest,
)
from opendirector.artifact import Artifact, Kind


@dataclass(frozen=True)
class LTXOptions:
    """Configuration for the LTX synchronous API."""

    api_base_url: str = "https://api.ltx.video"
    model: str = "ltx-2-3-fast"
    resolution: str | None = None
    fps: int = 24
    generate_audio: bool = True
    timeout_seconds: int = 900


class LTXAnimationProvider(AnimationProvider):
    """Real LTX image-to-video animation provider."""

    provider_id = "ltx.video"

    capabilities = AnimationCapabilities(
        text_to_video=False,
        image_to_video=True,
        audio_to_video=False,
        retake=False,
        first_last_frame=False,
        native_audio=True,
    )

    SUPPORTED_IMAGE_SUFFIXES = {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
    }

    FAST_DURATIONS = (
        6,
        8,
        10,
        12,
        14,
        16,
        18,
        20,
    )

    PRO_DURATIONS = (
        6,
        8,
        10,
    )

    def __init__(
        self,
        options: LTXOptions | None = None,
        prompt_builder: LTXPromptBuilder | None = None,
        session: requests.Session | None = None,
        api_key: str | None = None,
    ) -> None:
        self.options = options or LTXOptions()
        self.prompt_builder = prompt_builder or LTXPromptBuilder()
        self.session = session or requests.Session()
        self.api_key = api_key or os.getenv("LTX_API_KEY")

    async def animate(
        self,
        request: AnimationRequest,
    ) -> GeneratedClip:
        self.validate_request(request)
        self._validate_ltx_request(request)

        if not self.api_key:
            raise RuntimeError("LTX_API_KEY is not set")

        assert request.keyframe is not None

        duration = self._resolve_duration(request)
        resolution = self._resolve_resolution(request)
        prompt = self.prompt_builder.build(request.direction)

        request.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path = self._next_output_path(
            output_directory=request.output_directory,
            shot_id=request.shot_id,
        )

        payload: dict[str, Any] = {
            "image_uri": self._image_to_data_uri(request.keyframe.location),
            "prompt": prompt,
            "model": self.options.model,
            "duration": duration,
            "resolution": resolution,
            "generate_audio": (self.options.generate_audio),
        }

        # Include FPS only when explicitly useful to the API.
        if self.options.fps:
            payload["fps"] = self.options.fps

        response = self.session.post(
            (self.options.api_base_url.rstrip("/") + "/v1/image-to-video"),
            headers={
                "Authorization": (f"Bearer {self.api_key}"),
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=self.options.timeout_seconds,
        )

        if not response.ok:
            detail = response.text[:2000]

            raise RuntimeError(
                "LTX image-to-video request failed "
                f"with HTTP {response.status_code}: "
                f"{detail}"
            )

        content_type = response.headers.get(
            "Content-Type",
            "",
        )

        if "video" not in content_type.casefold() and not response.content.startswith(
            self._mp4_signature_prefix()
        ):
            raise RuntimeError(
                "LTX returned a successful response "
                "that does not appear to be video. "
                f"Content-Type: {content_type!r}; "
                f"body: {response.text[:1000]}"
            )

        output_path.write_bytes(response.content)

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
                "animation_mode": (request.mode.value),
                "source_keyframe_id": (request.keyframe.id),
                "duration_seconds": duration,
                "resolution": resolution,
                "fps": self.options.fps,
                "model": self.options.model,
                "has_audio": (self.options.generate_audio),
                "audio_baked_in": (self.options.generate_audio),
                "prompt": prompt,
                "request_id": response.headers.get("x-request-id"),
            },
        )

        return GeneratedClip(
            artifact=artifact,
            duration_seconds=float(duration),
            mode=request.mode,
            provider_id=self.provider_id,
            has_video=True,
            has_audio=self.options.generate_audio,
            audio_baked_in=(self.options.generate_audio),
            metadata={
                "model": self.options.model,
                "resolution": resolution,
                "fps": self.options.fps,
                "prompt": prompt,
                "reference_audio_used": False,
            },
        )

    def _validate_ltx_request(
        self,
        request: AnimationRequest,
    ) -> None:
        if request.mode is not AnimationMode.GENERATE:
            raise ValueError("LTX provider V1 currently supports " "GENERATE mode only")

        if request.keyframe is None:
            raise ValueError("LTX image-to-video requires a keyframe")

        if not request.keyframe.exists:
            raise FileNotFoundError(
                "LTX keyframe not found: " f"{request.keyframe.location}"
            )

        suffix = request.keyframe.location.suffix.casefold()

        if suffix not in self.SUPPORTED_IMAGE_SUFFIXES:
            raise ValueError(
                "LTX requires a raster keyframe "
                "such as PNG, JPEG, or WebP. "
                f"Received: {request.keyframe.location}"
            )

    def _resolve_duration(
        self,
        request: AnimationRequest,
    ) -> int:
        requested = request.duration_seconds

        if requested is None:
            metadata_value = request.direction.metadata.get("duration_seconds")

            if isinstance(
                metadata_value,
                int | float,
            ):
                requested = float(metadata_value)

        if requested is None:
            requested = 6.0

        allowed = (
            self.PRO_DURATIONS
            if self.options.model.endswith("-pro")
            else self.FAST_DURATIONS
        )

        requested_number = float(requested)

        return min(
            allowed,
            key=lambda value: abs(value - requested_number),
        )

    def _resolve_resolution(
        self,
        request: AnimationRequest,
    ) -> str:
        if self.options.resolution:
            return self.options.resolution

        orientation = request.production_specification.preferred_orientation.casefold()

        if orientation == "portrait":
            return "1080x1920"

        if orientation == "landscape":
            return "1920x1080"

        raise ValueError(
            "LTX-2.3 currently requires portrait "
            "9:16 or landscape 16:9 output. "
            f"Received orientation: {orientation!r}"
        )

    @staticmethod
    def _image_to_data_uri(
        path: Path,
    ) -> str:
        mime = mimetypes.guess_type(path)[0] or "image/png"
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")

        return f"data:{mime};base64,{encoded}"

    @staticmethod
    def _next_output_path(
        output_directory: Path,
        shot_id: str,
    ) -> Path:
        iteration = 1

        while True:
            candidate = output_directory / (
                f"{shot_id}-ltx-generate-" f"{iteration:03d}.mp4"
            )

            if not candidate.exists():
                return candidate

            iteration += 1

    @staticmethod
    def _mp4_signature_prefix() -> bytes:
        # MP4 normally contains "ftyp" starting at byte 4.
        return b"\x00\x00\x00"
