import asyncio

import pytest

from opendirector import Studio
from opendirector.creative import CreativeContext, CreativeProgram
from opendirector.creative.operators import (
    CandidateBlueprint,
    CreateCandidatesOperator,
    ReviewCandidatesOperator,
    SelectCandidateOperator,
)
from opendirector.crew import Editor
from opendirector.providers import MockLanguageProvider


def build_studio() -> Studio:
    studio = Studio("Gilbert Studio")
    provider = studio.providers.register(MockLanguageProvider())
    studio.crew.add(Editor(provider))
    return studio


def test_create_review_select_cycle():
    studio = build_studio()

    program = CreativeProgram(
        name="Opening Shot Cycle",
        operators=[
            CreateCandidatesOperator(
                purpose="Choose the opening shot",
                blueprints=[
                    CandidateBlueprint("Wide sunrise"),
                    CandidateBlueprint("Emotional close-up"),
                    CandidateBlueprint("Tracking reveal"),
                ],
            ),
            ReviewCandidatesOperator(studio.crew),
            SelectCandidateOperator(),
        ],
    )

    context = CreativeContext()
    result = asyncio.run(studio.run(program, context))

    candidate_set = result.candidate_set
    assert candidate_set is not None
    assert len(candidate_set.candidates) == 3

    assert result.metadata["completed_operators"] == [
        "create_candidates",
        "review_candidates",
        "select_candidate",
    ]

    assert result.metadata["created_candidate_count"] == 3
    assert result.metadata["reviewed_candidate_count"] == 3
    assert result.metadata["selected_candidate_title"] == "Emotional close-up"
    assert result.metadata["selected_candidate_score"] == 91

    winner = candidate_set.winner()
    assert winner is not None
    assert winner.title == "Emotional close-up"
    assert candidate_set.selected_id == winner.id


def test_select_requires_candidate_set():
    studio = build_studio()
    program = CreativeProgram(
        name="Invalid Selection",
        operators=[SelectCandidateOperator()],
    )

    with pytest.raises(ValueError, match="CandidateSet"):
        asyncio.run(studio.run(program, CreativeContext()))


def test_select_requires_reviewed_candidates():
    studio = build_studio()

    program = CreativeProgram(
        name="Unreviewed Selection",
        operators=[
            CreateCandidatesOperator(
                purpose="Choose a shot",
                blueprints=[
                    CandidateBlueprint("Candidate A"),
                    CandidateBlueprint("Candidate B"),
                ],
            ),
            SelectCandidateOperator(),
        ],
    )

    with pytest.raises(ValueError, match="reviewed before selection"):
        asyncio.run(studio.run(program, CreativeContext()))
