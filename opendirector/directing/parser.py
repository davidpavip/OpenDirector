from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from opendirector.directing.models import (
    DialogueDirection,
    ShotDirection,
)


@dataclass(frozen=True)
class ParsedDirectionDocument:
    """Parsed human-editable direction.md document."""

    direction: ShotDirection
    keyframe_path: str | None


class ShotDirectionMarkdownParser:
    """Parse the canonical direction.md format."""

    SECTION_NAMES = {
        "Shot & Camera": "shot_and_camera",
        "Subject & Action": "subject_and_action",
        "Performance & Emotion": ("performance_and_emotion"),
        "Lighting & Style": "lighting_and_style",
        "Narration": "narration",
        "Acoustic Environment": ("acoustic_environment"),
        "Motion Guidance": "motion_guidance",
        "Creative Notes": "creative_notes",
    }

    def parse(
        self,
        markdown: str,
        production_id: str,
    ) -> ParsedDirectionDocument:
        frontmatter, body = self._split_frontmatter(markdown)

        scene_id = frontmatter.get("scene", "")
        shot_id = frontmatter.get("shot", "")

        if not scene_id:
            raise ValueError("Direction document is missing scene")

        if not shot_id:
            raise ValueError("Direction document is missing shot")

        sections = self._parse_sections(body)
        dialogue = self._parse_dialogue(sections.get("Dialogue", ""))

        values: dict[str, str] = {}

        for heading, field_name in self.SECTION_NAMES.items():
            values[field_name] = self._clean_value(sections.get(heading, ""))

        direction = ShotDirection(
            production_id=production_id,
            scene_id=scene_id,
            shot_id=shot_id,
            keyframe_path=(frontmatter.get("keyframe") or None),
            dialogue=dialogue,
            status=frontmatter.get(
                "status",
                "draft",
            ),
            **values,
        )

        return ParsedDirectionDocument(
            direction=direction,
            keyframe_path=(frontmatter.get("keyframe") or None),
        )

    def parse_file(
        self,
        path: Path,
        production_id: str,
    ) -> ParsedDirectionDocument:
        if not path.is_file():
            raise FileNotFoundError(f"Direction document not found: {path}")

        return self.parse(
            path.read_text(encoding="utf-8"),
            production_id=production_id,
        )

    @staticmethod
    def _split_frontmatter(
        markdown: str,
    ) -> tuple[dict[str, str], str]:
        lines = markdown.splitlines()

        if not lines or lines[0].strip() != "---":
            return {}, markdown

        frontmatter: dict[str, str] = {}
        closing_index: int | None = None

        for index in range(1, len(lines)):
            line = lines[index]

            if line.strip() == "---":
                closing_index = index
                break

            if ":" not in line:
                continue

            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip()

        if closing_index is None:
            raise ValueError("Direction frontmatter is not closed")

        body = "\n".join(lines[closing_index + 1 :])

        return frontmatter, body

    @staticmethod
    def _parse_sections(
        body: str,
    ) -> dict[str, str]:
        sections: dict[str, list[str]] = {}
        current: str | None = None

        for line in body.splitlines():
            if line.startswith("## "):
                current = line[3:].strip()
                sections[current] = []
                continue

            if current is not None:
                sections[current].append(line)

        return {name: "\n".join(lines).strip() for name, lines in sections.items()}

    @staticmethod
    def _parse_dialogue(
        value: str,
    ) -> tuple[DialogueDirection, ...]:
        if not value:
            return ()

        if value.strip().casefold() in {
            "none",
            "none.",
            "not specified",
            "not specified.",
        }:
            return ()

        lines = value.splitlines()
        results: list[DialogueDirection] = []

        speaker: str | None = None
        text = ""
        delivery = ""

        def append_current() -> None:
            nonlocal speaker, text, delivery

            if speaker and text:
                results.append(
                    DialogueDirection(
                        speaker=speaker,
                        text=text.strip('"'),
                        delivery=delivery,
                    )
                )

            speaker = None
            text = ""
            delivery = ""

        for raw_line in lines:
            line = raw_line.strip()

            if line.startswith("### "):
                append_current()
                speaker = line[4:].strip()
                continue

            if not line:
                continue

            if line.casefold().startswith("delivery:"):
                delivery = line.split(
                    ":",
                    1,
                )[1].strip()
                continue

            if speaker and not text:
                text = line

        append_current()

        return tuple(results)

    @staticmethod
    def _clean_value(
        value: str,
    ) -> str:
        normalized = value.strip()

        if normalized.casefold() in {
            "none",
            "none.",
            "not specified",
            "not specified.",
        }:
            return ""

        return normalized
