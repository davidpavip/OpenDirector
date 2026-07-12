import asyncio

import pytest

from opendirector import Studio
from opendirector.core.candidate import Candidate, CandidateSet
from opendirector.creative import CreativeContext, CreativeProgram
from opendirector.creative.operators import ReviewCandidatesOperator
from opendirector.crew import Editor
from opendirector.providers import (
    LanguageRequest,
    MockLanguageProvider,
)


def test_studio_owns_provider_registry():
    studio = Studio("Gilbert Studio")

    assert len(studio.providers) == 0


def test_provider_registry_registers_provider():
    studio = Studio("Gilbert Studio")
    provider = studio.providers.register(MockLanguageProvider())

    assert studio.providers.has("mock.language")
    assert studio.providers.get("mock.language") is provider


def test_provider_registry_rejects_duplicate():
    studio = Studio("Gilbert Studio")
    studio.providers.register(MockLanguageProvider())

    with pytest.raises(ValueError, match="already registered"):
        studio.providers.register(MockLanguageProvider())


def test_mock_language_provider_returns_result():
    provider = MockLanguageProvider()

    result = asyncio.run(
        provider.generate(
            LanguageRequest(
                system_instruction="Review candidates.",
                user_message="Candidate A, Candidate B, Candidate C",
            )
        )
    )

    assert result.provider_id == "mock.language"
    assert result.model == "mock-language-v1"
    assert result.metadata["recommended_index"] == 1


def test_editor_reviews_through_registered_provider():
    studio = Studio("Gilbert Studio")
    provider = studio.providers.register(MockLanguageProvider())
    studio.crew.add(Editor(provider))

    candidates = CandidateSet(purpose="Choose opening shot")
    candidates.add(Candidate(candidate_type="shot", title="Wide sunrise"))
    candidates.add(Candidate(candidate_type="shot", title="Emotional close-up"))
    candidates.add(Candidate(candidate_type="shot", title="Tracking reveal"))

    context = CreativeContext(candidate_set=candidates)

    program = CreativeProgram(
        name="Provider Editorial Review",
        operators=[ReviewCandidatesOperator(studio.crew)],
    )

    result = asyncio.run(studio.run(program, context))

    assert result.metadata["review_provider"] == "mock.language"
    assert result.metadata["review_model"] == "mock-language-v1"
    assert result.metadata["reviewed_candidate_count"] == 3

    assert candidates.candidates[0].average_score == 72
    assert candidates.candidates[1].average_score == 91
    assert candidates.candidates[2].average_score == 83

    assert candidates.winner() == candidates.candidates[1]
