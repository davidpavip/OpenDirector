from __future__ import annotations

from abc import ABC, abstractmethod
from html import escape
from pathlib import Path
from textwrap import wrap

##from opendirector.sketching.models import (
##    SketchRequest,
##    SketchResult,
##)
##from opendirector.products import ProductType, SketchProduct

from opendirector.artifact import Artifact, Kind


class SketchProvider(ABC):
    """Provider capable of producing one visual sketch."""

    provider_id: str

    @abstractmethod
    async def sketch(
        self,
        request: SketchRequest,
    ) -> Artifact:
        raise NotImplementedError


class MockSketchProvider(SketchProvider):
    """Deterministic SVG provider for architecture validation.

    It creates a readable storyboard panel without calling an
    external image-generation service.
    """

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

        output_path.write_text(
            self._render_svg(request),
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
                "duration_seconds": request.shot.duration_seconds,
            },
        )

    def _render_svg(
        self,
        request: SketchRequest,
    ) -> str:
        shot = request.shot

        purpose_lines = self._lines(
            shot.purpose,
            width=55,
        )
        camera_lines = self._lines(
            f"Camera: {shot.camera or 'Not specified'}",
            width=55,
        )

        continuity = shot.continuity or "No additional continuity notes."
        continuity_lines = self._lines(
            f"Continuity: {continuity}",
            width=55,
        )

        revision = shot.filmmaker_revision.strip()
        if revision:
            revision_lines = self._lines(
                f"Filmmaker revision: {revision}",
                width=55,
            )
        else:
            revision_lines = []

        text_lines = (
            purpose_lines + [""] + camera_lines + continuity_lines + revision_lines
        )

        text_svg: list[str] = []
        y = 330

        for line in text_lines:
            text_svg.append(
                (
                    f'<text x="60" y="{y}" '
                    'font-family="sans-serif" '
                    'font-size="20" '
                    'fill="currentColor">'
                    f"{escape(line)}"
                    "</text>"
                )
            )
            y += 28

        return "\n".join(
            [
                '<svg xmlns="http://www.w3.org/2000/svg"',
                '     width="1280" height="720"',
                '     viewBox="0 0 1280 720">',
                '  <rect width="1280" height="720"',
                '        fill="#f4f4f4"/>',
                '  <rect x="40" y="40" width="1200" height="640"',
                '        rx="18" fill="white"',
                '        stroke="#222" stroke-width="4"/>',
                '  <rect x="60" y="80" width="1160" height="210"',
                '        fill="#dedede"',
                '        stroke="#555" stroke-width="2"/>',
                '  <line x1="60" y1="290" x2="1220" y2="80"',
                '        stroke="#999" stroke-width="2"/>',
                '  <line x1="60" y1="80" x2="1220" y2="290"',
                '        stroke="#999" stroke-width="2"/>',
                (
                    '  <text x="60" y="55" '
                    'font-family="sans-serif" '
                    'font-size="22" font-weight="bold">'
                    f"{escape(request.scene_title)}"
                    "</text>"
                ),
                (
                    '  <text x="1180" y="55" '
                    'text-anchor="end" '
                    'font-family="sans-serif" '
                    'font-size="20">'
                    f"{escape(shot.shot_id)}"
                    "</text>"
                ),
                (
                    '  <text x="640" y="195" '
                    'text-anchor="middle" '
                    'font-family="sans-serif" '
                    'font-size="28">'
                    "Storyboard sketch area"
                    "</text>"
                ),
                *[f"  {line}" for line in text_svg],
                (
                    '  <text x="60" y="650" '
                    'font-family="sans-serif" '
                    'font-size="18">'
                    f"Duration: {shot.duration_seconds:g} seconds"
                    "</text>"
                ),
                (
                    '  <text x="1220" y="650" '
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

    def _lines(
        self,
        value: str,
        width: int,
    ) -> list[str]:
        result: list[str] = []

        for paragraph in value.splitlines():
            normalized = paragraph.strip()

            if not normalized:
                continue

            result.extend(
                wrap(
                    normalized,
                    width=width,
                )
            )

        return result
