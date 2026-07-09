import pytest

from opendirector import Studio
from opendirector.core.movie import Movie
from opendirector.core.candidate import CandidateSet


def test_movie_requires_title():
    with pytest.raises(ValueError):
        Movie(title="")


def test_movie_can_hold_candidate_sets():
    movie = Movie(title="The Last Mountain")
    candidate_set = CandidateSet(purpose="Choose opening scene")

    movie.add_candidate_set(candidate_set)

    assert movie.candidate_sets[0] == candidate_set
    assert movie.to_dict()["candidate_sets"][0]["purpose"] == "Choose opening scene"


def test_studio_creates_movie():
    studio = Studio("Gilbert Studio")

    movie = studio.create_movie(
        title="The Last Mountain",
        description="A boy and a robot begin a mountain journey.",
    )

    assert movie.title == "The Last Mountain"
    assert movie in studio.movies
