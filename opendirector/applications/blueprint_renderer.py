from __future__ import annotations

from opendirector.planning import ProductionBlueprint
from opendirector.production import ProductionSpecification


class BlueprintMarkdownRenderer:
    """Render a ProductionBlueprint as portable Markdown."""

    @staticmethod
    def _render_production_specification(
        specification: ProductionSpecification,
    ) -> list[str]:
        duration = (
            f"{specification.target_duration_seconds} seconds"
            if specification.target_duration_seconds is not None
            else "Not specified"
        )

        subtitle_languages = ", ".join(
            specification.subtitle_languages
        )

        return [
            "## Production Specification",
            "",
            f"- Creative Profile: {specification.creative_profile}",
            (
                "- Distribution: "
                f"{specification.distribution or 'Not specified'}"
            ),
            (
                "- Orientation: "
                f"{specification.preferred_orientation}"
            ),
            f"- Aspect Ratio: {specification.aspect_ratio}",
            f"- Target Duration: {duration}",
            (
                "- Narration Language: "
                f"{specification.narration_language}"
            ),
            f"- Subtitle Languages: {subtitle_languages}",
            (
                "- Visual Style: "
                f"{specification.visual_style or 'Not specified'}"
            ),
            (
                "- Target Audience: "
                f"{specification.target_audience or 'Not specified'}"
            ),
            f"- Tone: {specification.tone or 'Not specified'}",
            "",
        ]

    def render(
        self,
        blueprint: ProductionBlueprint,
        production_specification: ProductionSpecification,
    ) -> str:
        lines: list[str] = [
            "# Production Blueprint",
            "",
            f"**Version:** {blueprint.version}",
            f"**Status:** {blueprint.status.value}",
            "",
        ]

        lines.extend(
            self._render_production_specification(
                production_specification
            )
        )

        lines.extend(
            [
                "## Intent",
                "",
                blueprint.intent_summary or "Not defined.",
                "",
                "## Story",
                "",
                blueprint.story_summary or "Not defined.",
                "",
                "## Story Roles",
                "",
            ]
        )

        self._append_story_roles(lines, blueprint)
        self._append_professions(lines, blueprint)
        self._append_assignments(lines, blueprint)
        self._append_style(lines, blueprint)
        self._append_constraints(lines, blueprint)
        self._append_approval(lines, blueprint)

        return "\n".join(lines).rstrip() + "\n"


    def _append_story_roles(
        self,
        lines: list[str],
        blueprint: ProductionBlueprint,
    ) -> None:
        if not blueprint.story_roles:
            lines.extend(["No story roles defined.", ""])
            return

        for role in blueprint.story_roles:
            lines.extend(
                [
                    f"### {role.name}",
                    "",
                    f"- **Importance:** {role.importance}",
                    (f"- **Purpose:** " f"{role.purpose or 'Not specified'}"),
                    "",
                ]
            )

    def _append_professions(
        self,
        lines: list[str],
        blueprint: ProductionBlueprint,
    ) -> None:
        lines.extend(["## Professions", ""])

        if not blueprint.professions:
            lines.extend(["No professions defined.", ""])
            return

        for profession in blueprint.professions:
            lines.extend(
                [
                    f"### {profession.name}",
                    "",
                ]
            )

            if profession.responsibilities:
                lines.append("Responsibilities:")

                for responsibility in profession.responsibilities:
                    lines.append(f"- {responsibility}")
            else:
                lines.append("Responsibilities not yet defined.")

            lines.append("")

    def _append_assignments(
        self,
        lines: list[str],
        blueprint: ProductionBlueprint,
    ) -> None:
        lines.extend(
            [
                "## Assignments",
                "",
                "| Profession | Mode | Performer |",
                "|---|---|---|",
            ]
        )

        if blueprint.assignments:
            for assignment in blueprint.assignments:
                lines.append(
                    f"| {assignment.profession_name} "
                    f"| {assignment.mode.value} "
                    f"| {assignment.performer or 'Unassigned'} |"
                )
        else:
            lines.append("| None | — | — |")

        lines.append("")

    def _append_style(
        self,
        lines: list[str],
        blueprint: ProductionBlueprint,
    ) -> None:
        lines.extend(["## Style", ""])

        if blueprint.style:
            for key, value in blueprint.style.items():
                label = key.replace("_", " ").title()
                lines.append(f"- **{label}:** {value}")
        else:
            lines.append("No style direction defined.")

        lines.append("")

    def _append_constraints(
        self,
        lines: list[str],
        blueprint: ProductionBlueprint,
    ) -> None:
        lines.extend(["## Constraints", ""])

        if blueprint.constraints:
            for constraint in blueprint.constraints:
                lines.append(f"- {constraint}")
        else:
            lines.append("No constraints defined.")

        lines.append("")

    def _append_approval(
        self,
        lines: list[str],
        blueprint: ProductionBlueprint,
    ) -> None:
        lines.extend(
            [
                "## Approval",
                "",
                (f"- **Approved by:** " f"{blueprint.approved_by or 'Pending'}"),
                (
                    f"- **Approved at:** " f"{blueprint.approved_at.isoformat()}"
                    if blueprint.approved_at is not None
                    else "- **Approved at:** Pending"
                ),
                "",
            ]
        )
