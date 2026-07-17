from __future__ import annotations

import re
from dataclasses import dataclass

from opendirector.sketching.models import SketchShot

_FIELD_HEADINGS = {
    "purpose": "Purpose",
    "camera": "Camera",
    "duration": "Estimated Duration",
    "output": "Intended Output",
    "continuity": "Continuity",
    "notes": "Creative Notes",
    "revision": "Filmmaker Revision",
}


@dataclass(frozen=True)
class ParsedShotDocument:
    scene_id: str
    scene_title: str
    shots: tuple[SketchShot, ...]


class ShotMarkdownParser:
    """Parse the canonical human-editable shots.md format."""

    _scene_pattern = re.compile(
        r"^scene:\s*(?P<value>.+?)\s*$",
        re.MULTILINE,
    )
    _title_pattern = re.compile(
        r"^title:\s*(?P<value>.+?)\s*$",
        re.MULTILINE,
    )
    _shot_heading_pattern = re.compile(
        r"^###\s+Shot\s+\d+\s+—\s+(?P<shot_id>[^\n]+)\s*$",
        re.MULTILINE,
    )

    def parse(self, markdown: str) -> ParsedShotDocument:
        scene_id = self._required_metadata(
            markdown,
            self._scene_pattern,
            "scene",
        )
        scene_title = self._required_metadata(
            markdown,
            self._title_pattern,
            "title",
        )

        matches = list(self._shot_heading_pattern.finditer(markdown))

        shots: list[SketchShot] = []

        for index, match in enumerate(matches):
            start = match.end()
            end = (
                matches[index + 1].start()
                if index + 1 < len(matches)
                else len(markdown)
            )

            block = markdown[start:end]
            shot_id = match.group("shot_id").strip()

            shots.append(
                SketchShot(
                    shot_id=shot_id,
                    purpose=self._required_section(
                        block,
                        _FIELD_HEADINGS["purpose"],
                    ),
                    camera=self._section(
                        block,
                        _FIELD_HEADINGS["camera"],
                    ),
                    duration_seconds=self._parse_duration(
                        self._required_section(
                            block,
                            _FIELD_HEADINGS["duration"],
                        )
                    ),
                    intended_output=self._section(
                        block,
                        _FIELD_HEADINGS["output"],
                    ),
                    continuity=self._section(
                        block,
                        _FIELD_HEADINGS["continuity"],
                    ),
                    creative_notes=self._section(
                        block,
                        _FIELD_HEADINGS["notes"],
                    ),
                    filmmaker_revision=self._section(
                        block,
                        _FIELD_HEADINGS["revision"],
                    ),
                )
            )

        return ParsedShotDocument(
            scene_id=scene_id,
            scene_title=scene_title,
            shots=tuple(shots),
        )

    def _required_metadata(
        self,
        markdown: str,
        pattern: re.Pattern[str],
        field_name: str,
    ) -> str:
        match = pattern.search(markdown)

        if match is None:
            raise ValueError(f"shots.md is missing metadata field: {field_name}")

        value = match.group("value").strip()

        if not value:
            raise ValueError(f"shots.md metadata field is empty: {field_name}")

        return value

    def _required_section(
        self,
        block: str,
        heading: str,
    ) -> str:
        value = self._section(block, heading)

        if not value:
            raise ValueError(f"Shot section is missing or empty: {heading}")

        return value

    def _section(
        self,
        block: str,
        heading: str,
    ) -> str:
        pattern = re.compile(
            rf"^####\s+{re.escape(heading)}\s*$" rf"(?P<body>.*?)" rf"(?=^####\s+|\Z)",
            re.MULTILINE | re.DOTALL,
        )

        match = pattern.search(block)

        if match is None:
            return ""

        return self._clean_section(match.group("body"))

    def _clean_section(self, value: str) -> str:
        lines: list[str] = []

        for line in value.strip().splitlines():
            stripped = line.strip()

            if stripped.startswith("<!--"):
                continue

            if stripped.endswith("-->"):
                continue

            if stripped == "---":
                continue

            lines.append(line.rstrip())

        return "\n".join(lines).strip()

    def _parse_duration(self, value: str) -> float:
        match = re.search(
            r"(?P<number>\d+(?:\.\d+)?)",
            value,
        )

        if match is None:
            raise ValueError(f"Cannot parse shot duration: {value!r}")

        duration = float(match.group("number"))

        if duration <= 0:
            raise ValueError("Shot duration must be greater than zero")

        return duration
