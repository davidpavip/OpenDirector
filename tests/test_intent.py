from dataclasses import FrozenInstanceError

import pytest

from opendirector import Studio
from opendirector.core.intent import Intent


def test_intent_is_immutable():
    intent = Intent(message="Never give up.")

    with pytest.raises(FrozenInstanceError):
        intent.message = "Changed"


def test_intent_evolves_with_lineage():
    original = Intent(
        audience="family",
        emotion="hope",
        message="Never give up.",
    )

    evolved = original.evolve(
        message="Hope through sacrifice.",
    )

    assert evolved.version == 2
    assert evolved.parent_id == original.id
    assert evolved.id != original.id
    assert evolved.message == "Hope through sacrifice."
    assert original.message == "Never give up."


def test_intent_to_dict():
    intent = Intent(
        audience="family",
        emotion="hope",
        message="Never give up.",
        constraints=("PG tone",),
        priorities=("Story", "Emotion"),
    )

    data = intent.to_dict()

    assert data["audience"] == "family"
    assert data["constraints"] == ["PG tone"]
    assert data["priorities"] == ["Story", "Emotion"]


def test_studio_creates_movie_with_intent():
    studio = Studio("Gilbert Studio")
    intent = Intent(message="Never give up.")

    movie = studio.create_movie(
        title="The Last Mountain",
        intent=intent,
    )

    assert movie.intent == intent
