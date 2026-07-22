from __future__ import annotations

from pathlib import Path

from opendirector.directing.models import ShotDirection


class ShotDirectionMarkdownRenderer:
    """Render ShotDirection as filmmaker-editable Markdown."""

    def render(
        self,
        direction: ShotDirection,
        production_root: Path | None = None,
    ) -> str:
        keyframe = self._display_path(
            direction.keyframe_path,
            production_root,
        )

        lines: list[str] = [
            "---",
            "artifact: shot-direction",
            f"scene: {direction.scene_id}",
            f"shot: {direction.shot_id}",
            f"status: {direction.status}",
            "editable_by: filmmaker",
            f"keyframe: {keyframe or ''}",
            "---",
            "",
            f"# {direction.shot_id} — Direction",
            "",
            "## Shot & Camera",
            "",
            direction.shot_and_camera or "Not specified.",
            "",
            "## Subject & Action",
            "",
            direction.subject_and_action or "Not specified.",
            "",
            "## Performance & Emotion",
            "",
            (direction.performance_and_emotion or "Not specified."),
            "",
            "## Lighting & Style",
            "",
            direction.lighting_and_style or "Not specified.",
            "",
            "## Dialogue",
            "",
        ]

        if direction.dialogue:
            for dialogue in direction.dialogue:
                lines.extend(
                    [
                        f"### {dialogue.speaker}",
                        "",
                        f'"{dialogue.text}"',
                        "",
                    ]
                )

                if dialogue.delivery:
                    lines.extend(
                        [
                            f"Delivery: {dialogue.delivery}",
                            "",
                        ]
                    )
        else:
            lines.extend(["None.", ""])

        lines.extend(
            [
                "## Narration",
                "",
                direction.narration or "None.",
                "",
                "## Acoustic Environment",
                "",
                (direction.acoustic_environment or "Not specified."),
                "",
                "## Motion Guidance",
                "",
                direction.motion_guidance or "Not specified.",
                "",
                "## Creative Notes",
                "",
                direction.creative_notes or "None.",
                "",
                "## Production Context",
                "",
                (
                    "- Duration: "
                    f"{direction.metadata.get('duration_seconds', 'Unknown')} "
                    "seconds"
                ),
                (
                    "- Orientation: "
                    f"{direction.metadata.get('orientation', 'Unknown')}"
                ),
                (
                    "- Aspect Ratio: "
                    f"{direction.metadata.get('aspect_ratio', 'Unknown')}"
                ),
                (
                    "- Distribution: "
                    f"{direction.metadata.get('distribution') or 'Not specified'}"
                ),
                (
                    "- Direction Provider: "
                    f"{direction.metadata.get('provider_id', 'Unknown')}"
                ),
                "",
            ]
        )

        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def _display_path(
        value: str | None,
        production_root: Path | None,
    ) -> str | None:
        if value is None:
            return None

        path = Path(value)

        if production_root is not None:
            try:
                return str(path.resolve().relative_to(production_root.resolve()))
            except ValueError:
                pass

        return str(path)
