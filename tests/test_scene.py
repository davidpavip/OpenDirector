import pytest

from opendirector.core.movie import Movie
from opendirector.core.scene import Scene
from opendirector.core.candidate import CandidateSet


def test_scene_requires_title():
    with pytest.raises(ValueError):
        Scene(title="", sequence=1)


def test_scene_requires_positive_sequence():
    with pytest.raises(ValueError):
        Scene(title="Opening", sequence=0)


def test_movie_creates_scene():
    movie = Movie(title="The Last Mountain")

    scene = movie.create_scene(
        title="Leaving Home",
        summary="The boy decides to leave the village.",
        goal="Audience feels hope and uncertainty.",
    )

    assert scene in movie.scenes
    assert scene.sequence == 1
    assert scene.title == "Leaving Home"


def test_movie_orders_scenes_by_sequence():
    movie = Movie(title="The Last Mountain")

    scene2 = movie.create_scene(title="Second", sequence=2)
    scene1 = movie.create_scene(title="First", sequence=1)

    assert movie.scenes == [scene1, scene2]


def test_scene_can_hold_candidate_sets():
    scene = Scene(title="Opening", sequence=1)
    candidate_set = CandidateSet(purpose="Choose opening shot style")

    scene.add_candidate_set(candidate_set)

    assert scene.candidate_sets[0] == candidate_set
    assert scene.to_dict()["candidate_sets"][0]["purpose"] == "Choose opening shot style"
