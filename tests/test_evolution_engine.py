import asyncio

from opendirector import Studio
from opendirector.core.creative_traits import CreativeTraits
from opendirector.creative import (
    CreativeContext,
    CreativeCycle,
    CreativeProgram,
    MaxIterationsCondition,
)
from opendirector.creative.operators import (
    CandidateBlueprint,
    CreateCandidatesOperator,
    EvolveCandidatesOperator,
    ReviewCandidatesOperator,
    RunEvolutionGenerationOperator,
    SelectCandidateOperator,
    TraitMutation,
)
from opendirector.crew import Editor
from opendirector.evolution import (
    EvolutionEngine,
    SeedThenEvolveStrategy,
)
from opendirector.providers import MockLanguageProvider


def build_studio() -> Studio:
    studio = Studio("Gilbert Studio")
    provider = studio.providers.register(MockLanguageProvider())
    studio.crew.add(Editor(provider))
    return studio


def test_engine_seeds_then_evolves():
    studio = build_studio()

    seed = CreateCandidatesOperator(
        purpose="Choose the opening shot",
        blueprints=[
            CandidateBlueprint("Wide sunrise"),
            CandidateBlueprint("Emotional close-up"),
            CandidateBlueprint("Tracking reveal"),
        ],
    )

    evolve = EvolveCandidatesOperator(
        mutations=[
            TraitMutation(
                name="more emotional",
                changes={"emotion": "deeper hope"},
            ),
            TraitMutation(
                name="more cinematic",
                changes={
                    "camera": "low-angle tracking",
                    "lighting": "blue-gold twilight",
                },
            ),
        ]
    )

    strategy = SeedThenEvolveStrategy(
        seed_operator=seed,
        evolve_operator=evolve,
        review_operator=ReviewCandidatesOperator(studio.crew),
        select_operator=SelectCandidateOperator(),
    )

    engine = EvolutionEngine(strategy)

    cycle = CreativeCycle(
        name="Opening Shot Evolution",
        operators=[RunEvolutionGenerationOperator(engine)],
        stopping_condition=MaxIterationsCondition(3),
    )

    program = CreativeProgram(
        name="Opening Shot Program",
        cycles=[cycle],
    )

    context = CreativeContext(
        metadata={
            "seed_creative_traits": CreativeTraits(
                camera="wide",
                lighting="golden sunrise",
                emotion="hope",
                pacing="gentle",
            ).to_dict()
        }
    )

    result = asyncio.run(studio.run(program, context))

    reports = result.metadata["generation_reports"]

    assert len(reports) == 3
    assert reports[0]["generation"] == 1
    assert reports[0]["mode"] == "seed"
    assert reports[1]["generation"] == 2
    assert reports[1]["mode"] == "evolve"
    assert reports[2]["generation"] == 3
    assert reports[2]["mode"] == "evolve"

    assert result.metadata["generation"] == 3
    assert result.candidate_set is not None
    assert result.candidate_set.selected_id is not None


def test_each_generation_runs_review_and_selection():
    studio = build_studio()

    engine = EvolutionEngine(
        SeedThenEvolveStrategy(
            seed_operator=CreateCandidatesOperator(
                purpose="Opening shot",
                blueprints=[
                    CandidateBlueprint("Wide sunrise"),
                    CandidateBlueprint("Emotional close-up"),
                    CandidateBlueprint("Tracking reveal"),
                ],
            ),
            evolve_operator=EvolveCandidatesOperator(
                mutations=[
                    TraitMutation(
                        name="slower",
                        changes={"pacing": "slow"},
                    ),
                    TraitMutation(
                        name="closer",
                        changes={"camera": "close-up"},
                    ),
                ]
            ),
            review_operator=ReviewCandidatesOperator(studio.crew),
            select_operator=SelectCandidateOperator(),
        )
    )

    program = CreativeProgram(
        name="Two Generation Program",
        cycles=[
            CreativeCycle(
                name="Evolution",
                operators=[RunEvolutionGenerationOperator(engine)],
                stopping_condition=MaxIterationsCondition(2),
            )
        ],
    )

    result = asyncio.run(studio.run(program, CreativeContext()))

    reports = result.metadata["generation_reports"]

    for report in reports:
        assert report["completed_operators"][-2:] == [
            "review_candidates",
            "select_candidate",
        ]
        assert report["selected_candidate_id"]


def test_generation_reports_preserve_lineage():
    studio = build_studio()

    engine = EvolutionEngine(
        SeedThenEvolveStrategy(
            seed_operator=CreateCandidatesOperator(
                purpose="Opening shot",
                blueprints=[
                    CandidateBlueprint("Wide sunrise"),
                    CandidateBlueprint("Emotional close-up"),
                    CandidateBlueprint("Tracking reveal"),
                ],
            ),
            evolve_operator=EvolveCandidatesOperator(
                mutations=[
                    TraitMutation(
                        name="cinematic variation",
                        changes={"camera": "tracking"},
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
                name="Lineage Program",
                cycles=[
                    CreativeCycle(
                        name="Evolution",
                        operators=[RunEvolutionGenerationOperator(engine)],
                        stopping_condition=MaxIterationsCondition(2),
                    )
                ],
            ),
            CreativeContext(),
        )
    )

    assert len(result.metadata["generation_reports"]) == 2
    assert len(result.metadata["generation_history"]) == 1

    history = result.metadata["generation_history"][0]

    assert history["generation"] == 2
    assert history["parent_candidate_id"] is not None
