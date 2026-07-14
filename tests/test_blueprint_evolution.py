import asyncio

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
from opendirector.evolution import (
    EvolutionEngine,
    SeedThenEvolveStrategy,
)
from opendirector.planning import (
    BlueprintMutation,
    BlueprintSeed,
    Profession,
    ProductionBlueprint,
    SourceDocument,
    StoryRole,
)
from opendirector.planning.operators import (
    ExtractSelectedBlueprintOperator,
    EvolveBlueprintsOperator,
    SeedBlueprintsOperator,
    blueprint_from_candidate,
)
from opendirector.providers import MockLanguageProvider


def build_studio() -> Studio:
    studio = Studio("Gilbert Studio")
    provider = studio.providers.register(MockLanguageProvider())
    studio.crew.add(Editor(provider))
    return studio


def build_template() -> ProductionBlueprint:
    return ProductionBlueprint(
        source=SourceDocument(
            title="The Little Robot",
            content="""
# Creative Brief

A lonely boy discovers an abandoned robot near a mountain village.
""",
        )
    )


def test_evolution_engine_evolves_blueprint_candidates():
    studio = build_studio()
    template = build_template()

    seed_operator = SeedBlueprintsOperator(
        template=template,
        seeds=[
            BlueprintSeed(
                title="Faithful family adventure",
                intent_summary=("Create a hopeful family animation."),
                story_summary=(
                    "A lonely boy repairs an abandoned robot " "and brings it home."
                ),
                story_roles=(
                    StoryRole(
                        name="Boy",
                        importance="primary",
                    ),
                    StoryRole(
                        name="Robot",
                        importance="primary",
                    ),
                ),
                professions=(
                    Profession(name="Director"),
                    Profession(name="Editor"),
                ),
            ),
            BlueprintSeed(
                title="Emotional friendship drama",
                intent_summary=("Create an emotional story about companionship."),
                story_summary=(
                    "A boy and a damaged robot help each other " "overcome loneliness."
                ),
                story_roles=(
                    StoryRole(
                        name="Boy",
                        importance="primary",
                    ),
                    StoryRole(
                        name="Robot",
                        importance="primary",
                    ),
                    StoryRole(
                        name="Mother",
                        importance="supporting",
                    ),
                ),
                professions=(
                    Profession(name="Director"),
                    Profession(name="Editor"),
                    Profession(name="Composer"),
                ),
            ),
            BlueprintSeed(
                title="Mystery in the mountain",
                intent_summary=("Create a mysterious animated adventure."),
                story_summary=(
                    "The boy discovers that the robot protects "
                    "a forgotten secret beneath the mountain."
                ),
                story_roles=(
                    StoryRole(
                        name="Boy",
                        importance="primary",
                    ),
                    StoryRole(
                        name="Robot",
                        importance="primary",
                    ),
                    StoryRole(
                        name="Village Elder",
                        importance="supporting",
                    ),
                ),
                professions=(
                    Profession(name="Director"),
                    Profession(name="Editor"),
                    Profession(name="Sound Designer"),
                ),
            ),
        ],
    )

    evolve_operator = EvolveBlueprintsOperator(
        mutations=[
            BlueprintMutation(
                name="Stronger emotional relationship",
                story_summary=(
                    "A lonely boy repairs an abandoned robot. "
                    "Their growing friendship restores hope to "
                    "the boy, the robot, and the fading village."
                ),
                add_story_roles=(
                    StoryRole(
                        name="Mother",
                        purpose=("Ground the boy's emotional journey."),
                    ),
                ),
                add_professions=(Profession(name="Composer"),),
                style_changes={
                    "tone": "warm and emotional",
                },
            ),
            BlueprintMutation(
                name="Simplified short-film version",
                story_summary=(
                    "A boy finds and repairs a robot, and the two "
                    "quietly walk toward the village together."
                ),
                remove_story_roles=(
                    "Village Elder",
                    "Mother",
                ),
                add_constraints=("Maximum duration: 8 minutes",),
            ),
        ]
    )

    engine = EvolutionEngine(
        SeedThenEvolveStrategy(
            seed_operator=seed_operator,
            evolve_operator=evolve_operator,
            review_operator=ReviewCandidatesOperator(studio.crew),
            select_operator=SelectCandidateOperator(),
        )
    )

    program = CreativeProgram(
        name="Blueprint Evolution Program",
        cycles=[
            CreativeCycle(
                name="Blueprint Evolution",
                operators=[RunEvolutionGenerationOperator(engine)],
                stopping_condition=MaxIterationsCondition(2),
            ),
            CreativeCycle(
                name="Extract Final Blueprint",
                operators=[ExtractSelectedBlueprintOperator()],
            ),
        ],
    )

    result = asyncio.run(
        studio.run(
            program,
            CreativeContext(),
        )
    )

    reports = result.metadata["generation_reports"]

    assert len(reports) == 2
    assert reports[0]["mode"] == "seed"
    assert reports[1]["mode"] == "evolve"

    selected_blueprint = result.metadata["selected_blueprint"]

    assert isinstance(
        selected_blueprint,
        ProductionBlueprint,
    )
    assert selected_blueprint.source == template.source
    assert result.metadata["generation"] == 2
    assert len(result.metadata["blueprint_generation_history"]) == 1


def test_blueprint_mutation_preserves_unmodified_fields():
    template = build_template()

    parent = BlueprintSeed(
        title="Parent",
        intent_summary="Create a hopeful animation.",
        story_summary="A boy finds a robot.",
        story_roles=(
            StoryRole(name="Boy"),
            StoryRole(name="Robot"),
        ),
        professions=(
            Profession(name="Director"),
            Profession(name="Editor"),
        ),
        style={
            "visual_style": "cinematic 3D",
            "lighting": "golden sunset",
        },
        constraints=("Family audience",),
    ).create_blueprint(template)

    mutation = BlueprintMutation(
        name="Blue twilight variation",
        style_changes={
            "lighting": "blue-gold twilight",
        },
        add_constraints=("No camera shake",),
    )

    child = mutation.apply(
        parent,
        generation=2,
    )

    assert child.intent_summary == parent.intent_summary
    assert child.story_summary == parent.story_summary
    assert child.story_roles == parent.story_roles
    assert child.professions == parent.professions

    assert child.style["visual_style"] == "cinematic 3D"
    assert child.style["lighting"] == "blue-gold twilight"

    assert child.constraints == (
        "Family audience",
        "No camera shake",
    )


def test_selected_candidate_contains_blueprint():
    studio = build_studio()
    template = build_template()

    engine = EvolutionEngine(
        SeedThenEvolveStrategy(
            seed_operator=SeedBlueprintsOperator(
                template=template,
                seeds=[
                    BlueprintSeed(
                        title="Plan A",
                        intent_summary="Intent A",
                        story_summary="Story A",
                    ),
                    BlueprintSeed(
                        title="Plan B",
                        intent_summary="Intent B",
                        story_summary="Story B",
                    ),
                    BlueprintSeed(
                        title="Plan C",
                        intent_summary="Intent C",
                        story_summary="Story C",
                    ),
                ],
            ),
            evolve_operator=EvolveBlueprintsOperator(
                mutations=[
                    BlueprintMutation(
                        name="Refined version",
                        story_summary="A refined story.",
                    )
                ]
            ),
            review_operator=ReviewCandidatesOperator(studio.crew),
            select_operator=SelectCandidateOperator(),
        )
    )

    result = asyncio.run(
        studio.run(
            CreativeProgram(
                name="One Generation Blueprint Test",
                cycles=[
                    CreativeCycle(
                        name="Blueprint Seed",
                        operators=[RunEvolutionGenerationOperator(engine)],
                    )
                ],
            ),
            CreativeContext(),
        )
    )

    candidate_set = result.candidate_set
    assert candidate_set is not None
    assert candidate_set.selected_id is not None

    selected = next(
        candidate
        for candidate in candidate_set.candidates
        if candidate.id == candidate_set.selected_id
    )

    blueprint = blueprint_from_candidate(selected)

    assert isinstance(blueprint, ProductionBlueprint)
    assert blueprint.story_summary in {
        "Story A",
        "Story B",
        "Story C",
    }
