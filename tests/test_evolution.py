from opendirector.core.candidate import Candidate, CandidateSet, ReviewerScore
from opendirector.evolution import EvolutionEngine


def test_evolution_keeps_best_candidate():
    a = Candidate(candidate_type="shot", title="Candidate A")
    b = Candidate(candidate_type="shot", title="Candidate B")

    a.add_score(ReviewerScore("Story Reviewer", "story", 70))
    b.add_score(ReviewerScore("Story Reviewer", "story", 95))

    candidates = CandidateSet(purpose="Choose opening shot")
    candidates.add(a)
    candidates.add(b)

    engine = EvolutionEngine()
    evolved = engine.evolve(candidates)

    winner = evolved.winner()

    assert winner is not None
    assert winner.title == "Candidate B - evolved"
    assert winner.payload["parent_candidate_id"] == b.id
    assert winner.payload["evolution_strategy"] == "keep_best"


def test_evolution_handles_empty_candidate_set():
    candidates = CandidateSet(purpose="Empty set")

    engine = EvolutionEngine()
    evolved = engine.evolve(candidates)

    assert evolved.candidates == []
    assert evolved.winner() is None
