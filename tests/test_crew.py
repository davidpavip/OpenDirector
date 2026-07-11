import asyncio

import pytest

from opendirector import Studio
from opendirector.core.candidate import Candidate, CandidateSet
from opendirector.creative import CreativeContext, CreativeProgram
from opendirector.creative.operators import ReviewCandidatesOperator
from opendirector.crew import Editor


def test_studio_owns_a_crew():
    studio = Studio("Gilbert Studio")

    assert len(studio.crew) == 0


def test_crew_adds_and_finds_editor():
    studio = Studio("Gilbert Studio")
    editor = studio.crew.add(Editor())

    assert studio.crew.has("editor")
    assert studio.crew["editor"] is editor


def test_crew_rejects_duplicate_role():
    studio = Studio("Gilbert Studio")
    studio.crew.add(Editor())

    with pytest.raises(ValueError, match="role already filled"):
        studio.crew.add(Editor())


def test_editor_reviews_candidate_set():
    studio = Studio("Gilbert Studio")
    studio.crew.add(Editor())

    candidates = CandidateSet(purpose="Choose the opening shot")
    candidates.add(Candidate(candidate_type="shot", title="Wide sunrise"))
    candidates.add(Candidate(candidate_type="shot", title="Emotional close-up"))
    candidates.add(Candidate(candidate_type="shot", title="Tracking shot"))

    context = CreativeContext(candidate_set=candidates)

    program = CreativeProgram(
        name="Editorial Review",
        operators=[ReviewCandidatesOperator(studio.crew)],
    )

    result = asyncio.run(studio.run(program, context))

    assert result.metadata["reviewed_by"] == "editor"
    assert result.metadata["reviewed_candidate_count"] == 3
    assert result.metadata["completed_operators"] == ["review_candidates"]

    for candidate in candidates.candidates:
        assert len(candidate.scores) == 1
        assert candidate.scores[0].category == "editing"


def test_editor_requires_candidates():
    studio = Studio("Gilbert Studio")
    studio.crew.add(Editor())

    program = CreativeProgram(
        name="Invalid Review",
        operators=[ReviewCandidatesOperator(studio.crew)],
    )

    with pytest.raises(ValueError, match="CandidateSet"):
        asyncio.run(studio.run(program, CreativeContext()))
