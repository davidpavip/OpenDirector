from __future__ import annotations

from opendirector import Studio
from opendirector.creative import (
    CreativeCycle,
    CreativeProgram,
    MaxIterationsCondition,
)
from opendirector.creative.operators import (
    ReviewCandidatesOperator,
    RunEvolutionGenerationOperator,
    SelectCandidateOperator,
)
from opendirector.evolution import (
    EvolutionEngine,
    SeedThenEvolveStrategy,
)
from opendirector.planning import (
    BlueprintMutation,
    BlueprintSeed,
    Profession,
    ProductionBlueprint,
    StoryRole,
)
from opendirector.planning.operators import (
    ExtractSelectedBlueprintOperator,
    EvolveBlueprintsOperator,
    SeedBlueprintsOperator,
)


def build_planning_program(
    studio: Studio,
    template: ProductionBlueprint,
) -> CreativeProgram:
    """Build the initial deterministic planning program.

    This first profile demonstrates blueprint evolution for the
    Little Robot production. Later, an AI planning profession will
    construct seeds and mutations from arbitrary source Markdown.
    """

    engine = EvolutionEngine(
        SeedThenEvolveStrategy(
            seed_operator=SeedBlueprintsOperator(
                template=template,
                seeds=_blueprint_seeds(),
            ),
            evolve_operator=EvolveBlueprintsOperator(
                mutations=_blueprint_mutations(),
            ),
            review_operator=ReviewCandidatesOperator(studio.crew),
            select_operator=SelectCandidateOperator(),
        )
    )

    return CreativeProgram(
        name="Production Planning",
        cycles=[
            CreativeCycle(
                name="Blueprint Evolution",
                operators=[
                    RunEvolutionGenerationOperator(engine),
                ],
                stopping_condition=MaxIterationsCondition(2),
            ),
            CreativeCycle(
                name="Extract Selected Blueprint",
                operators=[
                    ExtractSelectedBlueprintOperator(),
                ],
            ),
        ],
    )


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
                "Develop story structure",
                "Write scene action and dialogue",
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


def _blueprint_seeds() -> list[BlueprintSeed]:
    professions = default_professions()
    constraints = default_constraints()

    return [
        BlueprintSeed(
            title="Faithful Family Adventure",
            intent_summary=(
                "Create a hopeful family animation about friendship, "
                "repair, and the courage to move forward."
            ),
            story_summary=(
                "A lonely boy discovers and repairs an abandoned "
                "robot. Together they travel through a mountain "
                "valley toward a glowing village and gradually "
                "become true companions."
            ),
            story_roles=(
                StoryRole(
                    name="Boy",
                    purpose=(
                        "Primary protagonist whose loneliness and "
                        "courage drive the emotional journey."
                    ),
                    importance="primary",
                ),
                StoryRole(
                    name="Robot",
                    purpose=(
                        "Faithful companion whose recovery and "
                        "forgotten purpose create mystery."
                    ),
                    importance="primary",
                ),
                StoryRole(
                    name="Mother",
                    purpose=(
                        "Provides emotional grounding and a reason "
                        "for the boy to return home."
                    ),
                    importance="supporting",
                ),
            ),
            professions=professions,
            style={
                "visual_style": "cinematic 3D animation",
                "lighting": "golden sunset to blue twilight",
                "camera": "gentle and stable",
                "tone": "hopeful and emotional",
            },
            constraints=constraints,
        ),
        BlueprintSeed(
            title="Quiet Emotional Journey",
            intent_summary=(
                "Create an intimate animated short centered on "
                "loneliness, trust, and companionship."
            ),
            story_summary=(
                "A lonely boy repairs a damaged robot. Their quiet "
                "walk toward a distant village becomes a restrained "
                "story about learning to trust each other."
            ),
            story_roles=(
                StoryRole(
                    name="Boy",
                    purpose="Human center of the emotional story.",
                    importance="primary",
                ),
                StoryRole(
                    name="Robot",
                    purpose=("Companion reflecting the boy's isolation."),
                    importance="primary",
                ),
            ),
            professions=professions,
            style={
                "visual_style": "cinematic 3D animation",
                "lighting": "soft blue-gold twilight",
                "camera": "slow observational movement",
                "tone": "quiet, tender, and reflective",
            },
            constraints=constraints + ("Use minimal dialogue.",),
        ),
        BlueprintSeed(
            title="Mountain Mystery Adventure",
            intent_summary=(
                "Create a family mystery-adventure with emotional "
                "warmth and a strong sense of discovery."
            ),
            story_summary=(
                "After repairing an abandoned robot, a boy learns "
                "that it once protected the glowing mountain village. "
                "Their journey reveals traces of its forgotten mission."
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
                    purpose=("Connects the robot's forgotten past to " "the village."),
                    importance="supporting",
                ),
            ),
            professions=professions
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
                "lighting": ("golden dusk and mysterious village glow"),
                "camera": ("controlled tracking and wide landscape shots"),
                "tone": "hopeful mystery",
            },
            constraints=constraints,
        ),
    ]


def _blueprint_mutations() -> list[BlueprintMutation]:
    return [
        BlueprintMutation(
            name="Strengthen the Friendship",
            story_summary=(
                "A lonely boy repairs an abandoned robot. As they "
                "cross the mountain valley, each protects the other "
                "in small, gentle ways. Their growing friendship "
                "gives both of them the courage to enter the village."
            ),
            style_changes={
                "tone": ("warm, emotional, and quietly adventurous"),
            },
            add_constraints=("The relationship must drive every major scene.",),
        ),
        BlueprintMutation(
            name="Simplify for an Eight-Minute Short",
            story_summary=(
                "A boy finds and repairs a robot. During one evening "
                "walk toward the glowing village, they move from "
                "uncertainty to trust and companionship."
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
    ]
