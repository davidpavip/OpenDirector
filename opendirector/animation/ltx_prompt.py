from __future__ import annotations

from opendirector.directing import ShotDirection


class LTXPromptBuilder:
    """Translate OpenDirector shot direction into an LTX prompt."""

    def build(
        self,
        direction: ShotDirection,
    ) -> str:
        sections: list[str] = []

        self._append(
            sections,
            "Shot and Camera",
            direction.shot_and_camera,
        )
        self._append(
            sections,
            "Subject and Action",
            direction.subject_and_action,
        )
        self._append(
            sections,
            "Performance and Emotion",
            direction.performance_and_emotion,
        )
        self._append(
            sections,
            "Lighting and Style",
            direction.lighting_and_style,
        )

        if direction.dialogue:
            dialogue_lines: list[str] = []

            for line in direction.dialogue:
                sentence = f"{line.speaker} says clearly: " f'"{line.text}"'

                if line.delivery:
                    sentence += f" Delivery: {line.delivery}."

                dialogue_lines.append(sentence)

            self._append(
                sections,
                "Dialogue",
                " ".join(dialogue_lines),
            )

        self._append(
            sections,
            "Narration",
            direction.narration,
        )
        self._append(
            sections,
            "Audio and Ambience",
            direction.acoustic_environment,
        )
        self._append(
            sections,
            "Motion Guidance",
            direction.motion_guidance,
        )
        self._append(
            sections,
            "Creative Notes",
            direction.creative_notes,
        )

        prompt = "\n\n".join(sections).strip()

        if not prompt:
            raise ValueError("Cannot build an LTX prompt from empty shot direction")

        if len(prompt) > 5000:
            raise ValueError("LTX prompt exceeds the 5000-character limit")

        return prompt

    @staticmethod
    def _append(
        sections: list[str],
        heading: str,
        value: str,
    ) -> None:
        text = value.strip()

        if text:
            sections.append(f"[{heading}] {text}")
