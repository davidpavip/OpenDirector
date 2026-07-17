from __future__ import annotations

from opendirector.planning import ScenePlanning, ShotPlan


class ShotMarkdownRenderer:
    """Render a scene's shot plan as human-editable Markdown.

    shots.md describes creative intent only. It must not contain
    provider-specific prompts, model identifiers, render attempts,
    or execution status.
    """

    def render(self, scene: ScenePlanning) -> str:
        lines: list[str] = [
            "---",
            "artifact: shot-plan",
            f"scene: {scene.id}",
            f"title: {scene.title}",
            "status: draft",
            "editable_by: filmmaker",
            "---",
            "",
            f"# {scene.title} — Shot Plan",
            "",
            "<!--",
            "This document is the creative contract for the scene.",
            "The filmmaker may edit purpose, camera, duration,",
            "continuity, and notes before sketching or animation.",
            "-->",
            "",
            "## Scene Intent",
            "",
            scene.understanding.objective,
            "",
            "## Emotional Objective",
            "",
            (scene.understanding.emotional_objective or "Not specified."),
            "",
            "## Selected Direction",
            "",
        ]

        if scene.decision is None:
            lines.extend(
                [
                    "No scene direction has been selected yet.",
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    ", ".join(scene.decision.selected_idea_ids),
                    "",
                    scene.decision.reasoning,
                    "",
                ]
            )

        lines.extend(
            [
                "## Scene Continuity",
                "",
            ]
        )

        self._append_list(
            lines,
            scene.understanding.continuity_requirements,
            "No scene-level continuity requirements specified.",
        )

        lines.extend(
            [
                "",
                "## Shots",
                "",
            ]
        )

        if not scene.shots:
            lines.extend(
                [
                    "No shots have been planned.",
                    "",
                ]
            )
        else:
            for index, shot in enumerate(
                scene.shots,
                start=1,
            ):
                self._append_shot(
                    lines=lines,
                    shot=shot,
                    index=index,
                )

        lines.extend(
            [
                "## Filmmaker Notes",
                "",
                "<!-- Add scene-wide shot direction here. -->",
                "",
            ]
        )

        return "\n".join(lines).rstrip() + "\n"

    def _append_shot(
        self,
        lines: list[str],
        shot: ShotPlan,
        index: int,
    ) -> None:
        lines.extend(
            [
                f"### Shot {index:02d} — {shot.id}",
                "",
                f"<!-- shot:id={shot.id} -->",
                "",
                "#### Purpose",
                "",
                shot.purpose,
                "",
                "#### Camera",
                "",
                shot.camera or "Not specified.",
                "",
                "#### Estimated Duration",
                "",
                f"{shot.estimated_duration_seconds:g} seconds",
                "",
                "#### Intended Output",
                "",
                self._display_output_kind(shot.output_kind),
                "",
                "#### Continuity",
                "",
                "<!-- Add shot-specific continuity requirements here. -->",
                "",
                "#### Creative Notes",
                "",
            ]
        )

        if shot.notes:
            self._append_list(
                lines,
                shot.notes,
                "None.",
            )
        else:
            lines.append(
                "<!-- Add composition, movement, lighting, "
                "performance, or timing notes here. -->"
            )

        lines.extend(
            [
                "",
                "#### Filmmaker Revision",
                "",
                "<!-- Human edits in this section are authoritative. -->",
                "",
                "---",
                "",
            ]
        )

    def _append_list(
        self,
        lines: list[str],
        values: tuple[str, ...],
        empty_message: str,
    ) -> None:
        if not values:
            lines.append(empty_message)
            return

        for value in values:
            lines.append(f"- {value}")

    def _display_output_kind(
        self,
        value: str,
    ) -> str:
        normalized = value.strip().replace("_", " ")

        if not normalized:
            return "Not specified."

        return normalized.capitalize()
