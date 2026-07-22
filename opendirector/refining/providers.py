from __future__ import annotations

from abc import ABC, abstractmethod
from html import escape
from pathlib import Path

from opendirector.artifact import Artifact, Kind
from opendirector.refining.models import RefineRequest


class RefineProvider(ABC):
    """Provider capable of producing one keyframe artifact."""

    provider_id: str

    @abstractmethod
    async def refine(
        self,
        request: RefineRequest,
    ) -> Artifact:
        raise NotImplementedError


class MockRefineProvider(RefineProvider):
    """Deterministic keyframe provider for tests and local development."""

    provider_id = "mock.refine"

    async def refine(
        self,
        request: RefineRequest,
    ) -> Artifact:
        source = request.source_artifact

        if source.kind is not Kind.IMAGE:
            raise ValueError("Refine requires an image artifact")

        if not source.exists:
            raise FileNotFoundError(f"Source artifact not found: {source.location}")

        request.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path = self._next_output_path(
            output_directory=request.output_directory,
            shot_id=source.shot_id or "keyframe",
        )

        width, height = self._canvas_size(request.production_specification)

        output_path.write_text(
            self._render_svg(
                request=request,
                width=width,
                height=height,
            ),
            encoding="utf-8",
        )

        iteration = self._iteration_from_path(output_path)

        return Artifact(
            production_id=source.production_id,
            scene_id=source.scene_id,
            shot_id=source.shot_id,
            kind=Kind.IMAGE,
            location=output_path,
            media_type="image/svg+xml",
            metadata={
                "provider_id": self.provider_id,
                "role": "keyframe",
                "source_artifact_id": source.id,
                "source_location": str(source.location),
                "refinement_iteration": iteration,
                "creative_direction": (request.creative_direction),
                "orientation": (request.production_specification.preferred_orientation),
                "aspect_ratio": (request.production_specification.aspect_ratio),
                "canvas_width": width,
                "canvas_height": height,
            },
        )

    @staticmethod
    def _canvas_size(
        specification,
    ) -> tuple[int, int]:
        orientation = specification.preferred_orientation.casefold()

        if orientation == "portrait":
            return 540, 960

        if orientation == "square":
            return 720, 720

        return 960, 540

    @staticmethod
    def _next_output_path(
        output_directory: Path,
        shot_id: str,
    ) -> Path:
        iteration = 1

        while True:
            candidate = output_directory / f"{shot_id}-keyframe-{iteration:03d}.svg"

            if not candidate.exists():
                return candidate

            iteration += 1

    @staticmethod
    def _iteration_from_path(
        path: Path,
    ) -> int:
        return int(path.stem.rsplit("-", 1)[-1])

    def _render_svg(
        self,
        request: RefineRequest,
        width: int,
        height: int,
    ) -> str:
        source = request.source_artifact

        center_x = width / 2
        center_y = height / 2
        margin = max(24, min(width, height) // 16)

        direction = (
            request.creative_direction
            or "Preserve the composition and create an animation-ready image."
        )

        return "\n".join(
            [
                '<svg xmlns="http://www.w3.org/2000/svg"',
                f'     width="{width}" height="{height}"',
                f'     viewBox="0 0 {width} {height}">',
                (f'<rect width="{width}" ' f'height="{height}" fill="#ece7df"/>'),
                (
                    f'<rect x="{margin}" y="{margin}" '
                    f'width="{width - margin * 2}" '
                    f'height="{height - margin * 2}" '
                    'rx="20" fill="white" '
                    'stroke="#222" stroke-width="4"/>'
                ),
                (
                    f'<text x="{center_x}" '
                    f'y="{center_y - 30}" '
                    'text-anchor="middle" '
                    'font-family="sans-serif" '
                    'font-size="30" '
                    'font-weight="bold">'
                    "Animation Keyframe"
                    "</text>"
                ),
                (
                    f'<text x="{center_x}" '
                    f'y="{center_y + 15}" '
                    'text-anchor="middle" '
                    'font-family="sans-serif" '
                    'font-size="18">'
                    f"Source: {escape(source.location.name)}"
                    "</text>"
                ),
                (
                    f'<text x="{center_x}" '
                    f'y="{center_y + 55}" '
                    'text-anchor="middle" '
                    'font-family="sans-serif" '
                    'font-size="16">'
                    f"{escape(direction)}"
                    "</text>"
                ),
                "</svg>",
                "",
            ]
        )
