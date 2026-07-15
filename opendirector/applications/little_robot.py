from __future__ import annotations

import asyncio
from pathlib import Path

from opendirector import Studio
from opendirector.creative import (
    CreativeContext,
    CreativeCycle,
    CreativeProgram,
    MaxIterationsCondition,
)
from opendirector.creative.operators import (
    ReviewCandidatesOperator,
    RunEvolutionGenerationOperator,
    SelectCandidateOperator,
)
from opendirector.crew import Editor
from opendirector.evolution import EvolutionEngine, SeedThenEvolveStrategy
from opendirector.planning import (
    AssignmentMode,
    BlueprintMutation,
    BlueprintSeed,
    Profession,
    ProductionBlueprint,
    RoleAssignment,
    SourceDocument,
    StoryRole,
)
from opendirector.planning.operators import (
    ExtractSelectedBlueprintOperator,
    EvolveBlueprintsOperator,
    SeedBlueprintsOperator,
)
from opendirector.providers import MockLanguageProvider

PRODUCTION_DIR = Path("productions/little_robot")
SOURCE_PATH = PRODUCTION_DIR / "source.md"
BLUEPRINT_PATH = PRODUCTION_DIR / "blueprint.md"
HISTORY_DIR = PRODUCTION_DIR / "history"


def build_studio() -> Studio:
    studio = Studio("Gilbert Studio")

    provider = studio.providers.register(MockLanguageProvider())
    studio.crew.add(Editor(provider))

    return studio


def load_source() -> SourceDocument:
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(f"Source document not found: {SOURCE_PATH}")

    return SourceDocument(
        title="The Little Robot",
        content=SOURCE_PATH.read_text(encoding="utf-8"),
        metadata={
            "production_path": str(PRODUCTION_DIR),
            "input_format": "markdown",
        },
    )


def build_blueprint_template(
    source: SourceDocument,
) -> ProductionBlueprint:
    return ProductionBlueprint(source=source)


def build_evolution_engine(
    studio: Studio,
    template: ProductionBlueprint,
) -> EvolutionEngine:
    seed_operator = SeedBlueprintsOperator(
        template=template,
        seeds=[
            BlueprintSeed(
                title="Faithful Family Adventure",
                intent_summary=(
                    "Create a hopeful family animation about friendship, "
                    "repair, and the courage to move forward."
                ),
                story_summary=(
                    "A lonely boy discovers and repairs an abandoned robot. "
                    "Together they travel through the mountain valley toward "
                    "a glowing village, gradually becoming true companions."
                ),
                story_roles=(
                    StoryRole(
                        name="Boy",
                        purpose=(
                            "Primary protagonist whose loneliness and courage "
                            "drive the emotional journey."
                        ),
                        importance="primary",
                    ),
                    StoryRole(
                        name="Robot",
                        purpose=(
                            "Faithful companion whose recovery and forgotten "
                            "purpose create mystery and emotional growth."
                        ),
                        importance="primary",
                    ),
                    StoryRole(
                        name="Mother",
                        purpose=(
                            "Provides emotional grounding and a reason for "
                            "the boy to return home."
                        ),
                        importance="supporting",
                    ),
                ),
                professions=default_professions(),
                style={
                    "visual_style": "cinematic 3D animation",
                    "lighting": "golden sunset to blue twilight",
                    "camera": "gentle and stable",
                    "tone": "hopeful and emotional",
                },
                constraints=default_constraints(),
            ),
            BlueprintSeed(
                title="Quiet Emotional Journey",
                intent_summary=(
                    "Create an intimate animated short centered on loneliness, "
                    "trust, and companionship."
                ),
                story_summary=(
                    "A lonely boy repairs a damaged robot. Their quiet walk "
                    "toward the distant village becomes a restrained story "
                    "about two incomplete beings learning to trust each other."
                ),
                story_roles=(
                    StoryRole(
                        name="Boy",
                        purpose="Human center of the emotional story.",
                        importance="primary",
                    ),
                    StoryRole(
                        name="Robot",
                        purpose="Companion reflecting the boy's isolation.",
                        importance="primary",
                    ),
                ),
                professions=default_professions(),
                style={
                    "visual_style": "cinematic 3D animation",
                    "lighting": "soft blue-gold twilight",
                    "camera": "slow observational movement",
                    "tone": "quiet, tender, and reflective",
                },
                constraints=default_constraints() + ("Use minimal dialogue.",),
            ),
            BlueprintSeed(
                title="Mountain Mystery Adventure",
                intent_summary=(
                    "Create a family mystery-adventure with emotional warmth "
                    "and a sense of discovery."
                ),
                story_summary=(
                    "After repairing an abandoned robot, a boy learns that it "
                    "once protected the glowing mountain village. Their journey "
                    "reveals traces of the robot's forgotten mission."
                ),
                story_roles=(
                    StoryRole(
                        name="Boy",
                        purpose="Curious protagonist and emotional anchor.",
                        importance="primary",
                    ),
                    StoryRole(
                        name="Robot",
                        purpose="Companion carrying the central mystery.",
                        importance="primary",
                    ),
                    StoryRole(
                        name="Village Elder",
                        purpose=("Connects the robot's forgotten past to the village."),
                        importance="supporting",
                    ),
                ),
                professions=default_professions()
                + (
                    Profession(
                        name="Sound Designer",
                        responsibilities=(
                            "Create environmental atmosphere",
                            "Design the robot's sonic identity",
                        ),
                    ),
                ),
                style={
                    "visual_style": "cinematic 3D adventure",
                    "lighting": "golden dusk and mysterious village glow",
                    "camera": "controlled tracking and wide landscape shots",
                    "tone": "hopeful mystery",
                },
                constraints=default_constraints(),
            ),
        ],
    )

    evolve_operator = EvolveBlueprintsOperator(
        mutations=[
            BlueprintMutation(
                name="Strengthen the Friendship",
                story_summary=(
                    "A lonely boy repairs an abandoned robot. As they cross "
                    "the mountain valley, each protects the other in small, "
                    "gentle ways. Their growing friendship gives both of them "
                    "the courage to enter the glowing village."
                ),
                style_changes={
                    "tone": "warm, emotional, and quietly adventurous",
                },
                add_constraints=("The relationship must drive every major scene.",),
            ),
            BlueprintMutation(
                name="Simplify for an Eight-Minute Short",
                story_summary=(
                    "A boy finds and repairs a robot. During one evening walk "
                    "toward the glowing village, they move from uncertainty "
                    "to trust and companionship."
                ),
                remove_story_roles=(
                    "Mother",
                    "Village Elder",
                ),
                add_constraints=(
                    "Maximum duration: 8 minutes",
                    "Use no more than two primary speaking roles",
                ),
            ),
        ],
    )

    strategy = SeedThenEvolveStrategy(
        seed_operator=seed_operator,
        evolve_operator=evolve_operator,
        review_operator=ReviewCandidatesOperator(studio.crew),
        select_operator=SelectCandidateOperator(),
    )

    return EvolutionEngine(strategy)


def default_professions() -> tuple[Profession, ...]:
    return (
        Profession(
            name="Director",
            responsibilities=(
                "Protect the creative intent",
                "Approve major production decisions",
            ),
        ),
        Profession(
            name="Screenwriter",
            responsibilities=(
                "Develop the story structure",
                "Write dialogue and scene action",
            ),
        ),
        Profession(
            name="Cinematographer",
            responsibilities=(
                "Design camera language",
                "Define lighting and composition",
            ),
        ),
        Profession(
            name="Editor",
            responsibilities=(
                "Shape pacing",
                "Protect continuity and emotional rhythm",
            ),
        ),
        Profession(
            name="Animator",
            responsibilities=("Create character and environmental motion",),
        ),
        Profession(
            name="Composer",
            responsibilities=("Develop the musical language",),
        ),
    )


def default_constraints() -> tuple[str, ...]:
    return (
        "Family-friendly",
        "Do not glorify violence",
        "Preserve character identity",
        "Use the smallest effective cast",
    )


def default_assignments() -> tuple[RoleAssignment, ...]:
    return (
        RoleAssignment(
            profession_name="Director",
            mode=AssignmentMode.HUMAN,
            performer="Gilbert",
        ),
        RoleAssignment(
            profession_name="Screenwriter",
            mode=AssignmentMode.AI_ASSISTANT,
            performer="OpenDirector",
        ),
        RoleAssignment(
            profession_name="Cinematographer",
            mode=AssignmentMode.AI_ASSISTANT,
            performer="OpenDirector",
        ),
        RoleAssignment(
            profession_name="Editor",
            mode=AssignmentMode.AI_ASSISTANT,
            performer="OpenDirector",
        ),
        RoleAssignment(
            profession_name="Animator",
            mode=AssignmentMode.AI_DELEGATE,
            performer="OpenDirector",
        ),
        RoleAssignment(
            profession_name="Composer",
            mode=AssignmentMode.AI_DELEGATE,
            performer="OpenDirector",
        ),
    )


def render_blueprint(
    blueprint: ProductionBlueprint,
) -> str:
    lines = [
        "# Production Blueprint",
        "",
        f"**Version:** {blueprint.version}",
        f"**Status:** {blueprint.status.value}",
        "",
        "## Intent",
        "",
        blueprint.intent_summary,
        "",
        "## Story",
        "",
        blueprint.story_summary,
        "",
        "## Story Roles",
        "",
    ]

    if blueprint.story_roles:
        for role in blueprint.story_roles:
            lines.extend(
                [
                    f"### {role.name}",
                    "",
                    f"- **Importance:** {role.importance}",
                    f"- **Purpose:** {role.purpose or 'Not specified'}",
                    "",
                ]
            )
    else:
        lines.extend(["No story roles defined.", ""])

    lines.extend(
        [
            "## Professions",
            "",
        ]
    )

    if blueprint.professions:
        for profession in blueprint.professions:
            lines.append(f"### {profession.name}")
            lines.append("")

            if profession.responsibilities:
                lines.append("Responsibilities:")
                for responsibility in profession.responsibilities:
                    lines.append(f"- {responsibility}")
            else:
                lines.append("Responsibilities not yet defined.")

            lines.append("")
    else:
        lines.extend(["No professions defined.", ""])

    lines.extend(
        [
            "## Assignments",
            "",
            "| Profession | Mode | Performer |",
            "|---|---|---|",
        ]
    )

    for assignment in blueprint.assignments:
        lines.append(
            f"| {assignment.profession_name} "
            f"| {assignment.mode.value} "
            f"| {assignment.performer or 'Unassigned'} |"
        )

    lines.extend(
        [
            "",
            "## Style",
            "",
        ]
    )

    if blueprint.style:
        for key, value in blueprint.style.items():
            label = key.replace("_", " ").title()
            lines.append(f"- **{label}:** {value}")
    else:
        lines.append("No style direction defined.")

    lines.extend(
        [
            "",
            "## Constraints",
            "",
        ]
    )

    if blueprint.constraints:
        for constraint in blueprint.constraints:
            lines.append(f"- {constraint}")
    else:
        lines.append("No constraints defined.")

    lines.extend(
        [
            "",
            "## Approval",
            "",
            f"- **Approved by:** {blueprint.approved_by or 'Pending'}",
            (
                f"- **Approved at:** {blueprint.approved_at.isoformat()}"
                if blueprint.approved_at is not None
                else "- **Approved at:** Pending"
            ),
            "",
        ]
    )

    return "\n".join(lines)


async def main() -> None:
    studio = build_studio()
    source = load_source()
    template = build_blueprint_template(source)
    engine = build_evolution_engine(studio, template)

    program = CreativeProgram(
        name="Little Robot Planning",
        cycles=[
            CreativeCycle(
                name="Blueprint Evolution",
                operators=[
                    RunEvolutionGenerationOperator(engine),
                ],
                stopping_condition=MaxIterationsCondition(2),
            ),
            CreativeCycle(
                name="Extract Blueprint",
                operators=[
                    ExtractSelectedBlueprintOperator(),
                ],
            ),
        ],
    )

    result = await studio.run(
        program,
        CreativeContext(),
    )

    draft = result.metadata.get("selected_blueprint")

    if not isinstance(draft, ProductionBlueprint):
        raise RuntimeError("Planning did not produce a blueprint")

    # Human approval boundary.
    approved = draft.approve("Gilbert")

    # Assignments are added after selecting the preferred blueprint.
    from dataclasses import replace

    available = {p.name for p in approved.professions}

    assignments = tuple(
        assignment
        for assignment in default_assignments()
        if assignment.profession_name in available
    )

    approved = replace(
        approved,
        assignments=assignments,
    )

    markdown = render_blueprint(approved)

    PRODUCTION_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    BLUEPRINT_PATH.write_text(markdown, encoding="utf-8")

    history_path = HISTORY_DIR / f"blueprint_v{approved.version}.md"
    history_path.write_text(markdown, encoding="utf-8")

    print(markdown)
    print()
    print(f"Saved: {BLUEPRINT_PATH}")
    print(f"Saved: {history_path}")


if __name__ == "__main__":
    asyncio.run(main())
