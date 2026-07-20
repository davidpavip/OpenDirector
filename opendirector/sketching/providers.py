from __future__ import annotations

from abc import ABC, abstractmethod
from html import escape
from pathlib import Path

from opendirector.artifact import Artifact, Kind
from opendirector.production import ProductionSpecification
from opendirector.sketching.models import SketchRequest


class SketchProvider(ABC):
    """Provider capable of producing one visual sketch artifact."""

    provider_id: str

    @abstractmethod
    async def sketch(
        self,
        request: SketchRequest,
    ) -> Artifact:
        """Create one sketch artifact from a provider-neutral request."""

        raise NotImplementedError


class MockSketchProvider(SketchProvider):
    """Deterministic SVG sketch provider used by tests and local demos."""

    provider_id = "mock.sketch"

    async def sketch(
        self,
        request: SketchRequest,
    ) -> Artifact:
        request.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path = request.output_directory / f"{request.shot.shot_id}.svg"

        width, height = self._canvas_size(request.production_specification)

        svg = self._render_svg(
            request=request,
            width=width,
            height=height,
        )

        output_path.write_text(
            svg,
            encoding="utf-8",
        )

        return Artifact(
            production_id=request.production_id,
            scene_id=request.scene_id,
            shot_id=request.shot.shot_id,
            kind=Kind.IMAGE,
            location=output_path,
            media_type="image/svg+xml",
            metadata={
                "provider_id": self.provider_id,
                "camera": request.shot.camera,
                "duration_seconds": (request.shot.duration_seconds),
                "orientation": (request.production_specification.preferred_orientation),
                "aspect_ratio": (request.production_specification.aspect_ratio),
                "canvas_width": width,
                "canvas_height": height,
            },
        )

    @staticmethod
    def _canvas_size(
        specification: ProductionSpecification,
    ) -> tuple[int, int]:
        orientation = specification.preferred_orientation.casefold()

        if orientation == "portrait":
            return 540, 960

        if orientation == "square":
            return 720, 720

        return 960, 540

    def _render_svg(
        self,
        request: SketchRequest,
        width: int,
        height: int,
    ) -> str:
        shot = request.shot

        outer_margin = max(
            24,
            min(width, height) // 18,
        )
        header_height = max(
            48,
            min(width, height) // 10,
        )
        footer_height = max(
            52,
            min(width, height) // 10,
        )

        frame_x = outer_margin
        frame_y = outer_margin
        frame_width = width - (outer_margin * 2)
        frame_height = height - (outer_margin * 2)

        image_x = frame_x + 20
        image_y = frame_y + header_height
        image_width = frame_width - 40
        image_height = frame_height - header_height - footer_height

        image_right = image_x + image_width
        image_bottom = image_y + image_height
        center_x = image_x + (image_width / 2)
        center_y = image_y + (image_height / 2)

        title_y = frame_y + 30
        footer_y = frame_y + frame_height - 20

        text_start_y = image_y + 34
        text_line_height = 24

        descriptive_lines = self._descriptive_lines(request)

        text_svg = []

        for index, line in enumerate(descriptive_lines):
            text_svg.append(
                (
                    f'<text x="{image_x + 20}" '
                    f'y="{text_start_y + index * text_line_height}" '
                    'font-family="sans-serif" '
                    'font-size="16">'
                    f"{escape(line)}"
                    "</text>"
                )
            )

        return "\n".join(
            [
                '<svg xmlns="http://www.w3.org/2000/svg"',
                (f'     width="{width}" ' f'height="{height}"'),
                (f'     viewBox="0 0 ' f'{width} {height}">'),
                (f'  <rect width="{width}" ' f'height="{height}" ' 'fill="#f4f4f4"/>'),
                (
                    f'  <rect x="{frame_x}" '
                    f'y="{frame_y}" '
                    f'width="{frame_width}" '
                    f'height="{frame_height}" '
                    'rx="18" '
                    'fill="white" '
                    'stroke="#222" '
                    'stroke-width="4"/>'
                ),
                (
                    f'  <rect x="{image_x}" '
                    f'y="{image_y}" '
                    f'width="{image_width}" '
                    f'height="{image_height}" '
                    'fill="#dedede" '
                    'stroke="#555" '
                    'stroke-width="2"/>'
                ),
                (
                    f'  <line x1="{image_x}" '
                    f'y1="{image_y}" '
                    f'x2="{image_right}" '
                    f'y2="{image_bottom}" '
                    'stroke="#999" '
                    'stroke-width="2"/>'
                ),
                (
                    f'  <line x1="{image_x}" '
                    f'y1="{image_bottom}" '
                    f'x2="{image_right}" '
                    f'y2="{image_y}" '
                    'stroke="#999" '
                    'stroke-width="2"/>'
                ),
                (
                    f'  <text x="{frame_x + 20}" '
                    f'y="{title_y}" '
                    'font-family="sans-serif" '
                    'font-size="22" '
                    'font-weight="bold">'
                    f"{escape(request.scene_title)}"
                    "</text>"
                ),
                (
                    f'  <text x="{frame_x + frame_width - 20}" '
                    f'y="{title_y}" '
                    'text-anchor="end" '
                    'font-family="sans-serif" '
                    'font-size="20">'
                    f"{escape(shot.shot_id)}"
                    "</text>"
                ),
                (
                    f'  <text x="{center_x}" '
                    f'y="{center_y}" '
                    'text-anchor="middle" '
                    'font-family="sans-serif" '
                    'font-size="28">'
                    "Storyboard sketch area"
                    "</text>"
                ),
                *[f"  {line}" for line in text_svg],
                (
                    f'  <text x="{frame_x + 20}" '
                    f'y="{footer_y}" '
                    'font-family="sans-serif" '
                    'font-size="18">'
                    f"Duration: "
                    f"{shot.duration_seconds:g} seconds"
                    "</text>"
                ),
                (
                    f"  <text "
                    f'x="{frame_x + frame_width - 20}" '
                    f'y="{footer_y}" '
                    'text-anchor="end" '
                    'font-family="sans-serif" '
                    'font-size="18">'
                    f"Provider: {self.provider_id}"
                    "</text>"
                ),
                "</svg>",
                "",
            ]
        )

    @staticmethod
    def _descriptive_lines(
        request: SketchRequest,
    ) -> tuple[str, ...]:
        shot = request.shot

        lines = [
            f"Purpose: {shot.purpose}",
            f"Camera: {shot.camera}",
        ]

        if shot.intended_output:
            lines.append(f"Output: {shot.intended_output}")

        if shot.continuity:
            lines.append(f"Continuity: {shot.continuity}")

        if shot.creative_notes:
            lines.append(f"Creative notes: {shot.creative_notes}")

        if shot.filmmaker_revision:
            lines.append("Filmmaker revision: " f"{shot.filmmaker_revision}")

        specification = request.production_specification

        lines.extend(
            [
                ("Orientation: " f"{specification.preferred_orientation}"),
                ("Aspect ratio: " f"{specification.aspect_ratio}"),
            ]
        )

        if request.style_context:
            lines.append(f"Style: {request.style_context}")

        return tuple(lines)
