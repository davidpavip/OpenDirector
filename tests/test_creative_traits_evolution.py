import asyncio

from opendirector import Studio
from opendirector.core.candidate import Candidate, CandidateSet
from opendirector.core.creative_traits import CreativeTraits
from opendirector.creative import (
    CreativeContext,
    CreativeCycle,
    CreativeProgram,
)
from opendirector.creative.operators import (
    EvolveCandidatesOperator,
    TraitMutation,
)


def test_creative_traits_are_immutable():
    original = CreativeTraits(
        camera="slow tracking",
        lighting="golden sunset",
        emotion="hope",
    )

    evolved = original.evolve(
        camera="low-angle tracking",
        emotion="determination",
    )

    assert original.camera == "slow tracking"
    assert original.emotion == "hope"

    assert evolved.camera == "low-angle tracking"
    assert evolved.emotion == "determination"
    assert evolved.lighting == "golden sunset"


def test_evolve_candidates_creates_next_generation():
    studio = Studio("Gilbert Studio")

    traits = CreativeTraits(
        camera="slow tracking",
        lighting="golden sunset",
        emotion="hope",
        pacing="gentle",
    )

    parent = Candidate(
        candidate_type="shot",
        title="Boy and robot descend the hill",
        created_by="seed",
        payload={
            "generation": 1,
            "creative_traits": traits.to_dict(),
        },
    )

    candidates = CandidateSet(purpose="Choose the hill descent shot")
    candidates.add(parent)
    candidates.select(parent.id)

    cycle = CreativeCycle(
        name="Trait Evolution",
        operators=[
            EvolveCandidatesOperator(
                mutations=[
                    TraitMutation(
                        name="slower and more emotional",
                        changes={
                            "pacing": "very slow",
                            "emotion": "tender hope",
                        },
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
        ],
    )

    program = CreativeProgram(
        name="Creative Trait Evolution",
        cycles=[cycle],
    )

    context = CreativeContext(candidate_set=candidates)
    result = asyncio.run(studio.run(program, context))

    evolved_set = result.candidate_set

    assert evolved_set is not None
    assert len(evolved_set.candidates) == 3
    assert result.metadata["generation"] == 2
    assert result.metadata["evolution_parent_id"] == parent.id

    elite = evolved_set.candidates[0]
    conservative = evolved_set.candidates[1]
    cinematic = evolved_set.candidates[2]

    assert elite.payload["evolution_operation"] == "elite_preservation"
    assert elite.payload["parent_candidate_ids"] == [parent.id]

    conservative_traits = CreativeTraits.from_dict(
        conservative.payload["creative_traits"]
    )
    assert conservative_traits.pacing == "very slow"
    assert conservative_traits.emotion == "tender hope"
    assert conservative_traits.lighting == "golden sunset"

    cinematic_traits = CreativeTraits.from_dict(cinematic.payload["creative_traits"])
    assert cinematic_traits.camera == "low-angle tracking"
    assert cinematic_traits.lighting == "blue-gold twilight"
    assert cinematic_traits.emotion == "hope"


def test_generation_history_is_recorded():
    studio = Studio("Gilbert Studio")

    parent = Candidate(
        candidate_type="shot",
        title="Opening shot",
        payload={
            "generation": 1,
            "creative_traits": CreativeTraits(
                camera="wide",
                emotion="wonder",
            ).to_dict(),
        },
    )

    candidates = CandidateSet(purpose="Opening shot")
    candidates.add(parent)
    candidates.select(parent.id)

    program = CreativeProgram(
        name="Lineage Program",
        cycles=[
            CreativeCycle(
                name="Evolution",
                operators=[
                    EvolveCandidatesOperator(
                        mutations=[
                            TraitMutation(
                                name="closer framing",
                                changes={"camera": "medium close-up"},
                            )
                        ]
                    )
                ],
            )
        ],
    )

    result = asyncio.run(
        studio.run(
            program,
            CreativeContext(candidate_set=candidates),
        )
    )

    history = result.metadata["generation_history"]

    assert len(history) == 1
    assert history[0]["generation"] == 2
    assert history[0]["parent_candidate_id"] == parent.id
    assert len(history[0]["candidate_ids"]) == 2
