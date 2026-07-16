from __future__ import annotations

from opendirector.planning import (
    PlanningDocument,
    ScenePlanning,
)


class PlanningMarkdownRenderer:
    """Render scene-centered planning as editable Markdown."""

    def render(self, document: PlanningDocument) -> str:
        lines: list[str] = [
            "---",
            "artifact: planning",
            f"production: {document.production_id}",
            f"status: {document.status}",
            "format: scene-centered",
            "---",
            "",
            f"# {document.title} — Production Planning",
            "",
            "## Production Understanding",
            "",
            "### Intent",
            "",
            document.understanding.intent,
            "",
            "### Audience",
            "",
        ]

        self._append_list(
            lines,
            document.understanding.audience,
            "Not specified.",
        )

        lines.extend(["", "### Target Runtime", ""])
        lines.append(document.understanding.target_runtime or "Not specified.")

        lines.extend(["", "### Themes", ""])
        self._append_list(
            lines,
            document.understanding.themes,
            "Not specified.",
        )

        lines.extend(["", "### Governing Values", ""])
        self._append_list(
            lines,
            document.understanding.values,
            "No explicit values supplied.",
        )

        lines.extend(["", "### Global Constraints", ""])
        self._append_list(
            lines,
            document.understanding.constraints,
            "No global constraints supplied.",
        )

        lines.extend(["", "### Open Questions", ""])
        self._append_list(
            lines,
            document.understanding.unknowns,
            "None.",
        )

        lines.extend(
            [
                "",
                "### Confidence",
                "",
                f"{document.understanding.confidence:.2f}",
                "",
            ]
        )

        for scene in document.scenes:
            self._append_scene(lines, scene)

        return "\n".join(lines).rstrip() + "\n"

    def _append_scene(
        self,
        lines: list[str],
        scene: ScenePlanning,
    ) -> None:
        lines.extend(
            [
                "---",
                "",
                f"# {scene.id} — {scene.title}",
                "",
                f"<!-- scene:id={scene.id} -->",
                f"<!-- status:{scene.status} -->",
                "",
                "## Understanding",
                "",
                "### Scene Objective",
                "",
                scene.understanding.objective,
                "",
                "### Emotional Objective",
                "",
                (scene.understanding.emotional_objective or "Not specified."),
                "",
                "### Story Function",
                "",
                (scene.understanding.story_function or "Not specified."),
                "",
                "### Required Story Information",
                "",
            ]
        )

        self._append_list(
            lines,
            scene.understanding.required_information,
            "None specified.",
        )

        lines.extend(["", "### Continuity Requirements", ""])
        self._append_list(
            lines,
            scene.understanding.continuity_requirements,
            "None specified.",
        )

        lines.extend(["", "### Constraints", ""])
        self._append_list(
            lines,
            scene.understanding.constraints,
            "None specified.",
        )

        lines.extend(["", "### Assumptions", ""])
        self._append_list(
            lines,
            scene.understanding.assumptions,
            "None.",
        )

        lines.extend(["", "### Unknowns", ""])
        self._append_list(
            lines,
            scene.understanding.unknowns,
            "None.",
        )

        lines.extend(["", "### Risks", ""])
        self._append_list(
            lines,
            scene.understanding.risks,
            "None.",
        )

        lines.extend(
            [
                "",
                "### Understanding Confidence",
                "",
                f"{scene.understanding.confidence:.2f}",
                "",
                "## Ideas",
                "",
            ]
        )

        if scene.ideas:
            for idea in scene.ideas:
                lines.extend(
                    [
                        f"### {idea.id} — {idea.title}",
                        "",
                        idea.description,
                        "",
                    ]
                )
        else:
            lines.extend(["Pending.", ""])

        lines.extend(["## Critique", ""])

        if scene.critiques:
            idea_titles = {idea.id: idea.title for idea in scene.ideas}

            for critique in scene.critiques:
                title = idea_titles.get(
                    critique.idea_id,
                    critique.idea_id,
                )

                lines.extend(
                    [
                        f"### {critique.idea_id} — {title}",
                        "",
                        "#### Strengths",
                        "",
                    ]
                )
                self._append_list(
                    lines,
                    critique.strengths,
                    "None recorded.",
                )

                lines.extend(["", "#### Weaknesses", ""])
                self._append_list(
                    lines,
                    critique.weaknesses,
                    "None recorded.",
                )

                lines.extend(["", "#### Risks", ""])
                self._append_list(
                    lines,
                    critique.risks,
                    "None recorded.",
                )
                lines.append("")
        else:
            lines.extend(["Pending.", ""])

        lines.extend(["## Decision", ""])

        if scene.decision is not None:
            lines.extend(
                [
                    "### Selected Direction",
                    "",
                    ", ".join(scene.decision.selected_idea_ids),
                    "",
                    "### Reasoning",
                    "",
                    scene.decision.reasoning,
                    "",
                    "### Confidence",
                    "",
                    f"{scene.decision.confidence:.2f}",
                    "",
                ]
            )
        else:
            lines.extend(["Pending.", ""])

        lines.extend(["## Shot Plan", ""])

        if scene.shots:
            for shot in scene.shots:
                lines.extend(
                    [
                        f"### {shot.id}",
                        "",
                        f"- **Purpose:** {shot.purpose}",
                        f"- **Camera:** {shot.camera}",
                        (
                            "- **Estimated Duration:** "
                            f"{shot.estimated_duration_seconds:g} seconds"
                        ),
                        f"- **Output:** {shot.output_kind}",
                    ]
                )

                if shot.notes:
                    lines.append("- **Notes:**")
                    for note in shot.notes:
                        lines.append(f"  - {note}")

                lines.append("")
        else:
            lines.extend(["Pending.", ""])

        lines.extend(
            [
                "## Filmmaker Notes",
                "",
                (
                    scene.filmmaker_notes
                    if scene.filmmaker_notes.strip()
                    else "<!-- Human filmmaker may edit here. -->"
                ),
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
