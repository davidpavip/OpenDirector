from opendirector.core.candidate import Candidate, CandidateSet, ReviewerScore, CandidateStatus


def test_candidate_average_score():
    c = Candidate(candidate_type="shot", title="Wide sunset shot")
    c.add_score(ReviewerScore("Story Reviewer", "story", 90))
    c.add_score(ReviewerScore("Emotion Reviewer", "emotion", 80))

    assert c.average_score == 85


def test_score_validation():
    try:
        ReviewerScore("Bad Reviewer", "story", 101)
        assert False
    except ValueError:
        assert True


def test_candidate_set_winner_by_score():
    a = Candidate(candidate_type="shot", title="Candidate A")
    b = Candidate(candidate_type="shot", title="Candidate B")

    a.add_score(ReviewerScore("Reviewer", "story", 80))
    b.add_score(ReviewerScore("Reviewer", "story", 95))

    s = CandidateSet(purpose="Choose best opening shot")
    s.add(a)
    s.add(b)

    assert s.winner() == b


def test_candidate_set_select():
    a = Candidate(candidate_type="shot", title="Candidate A")
    s = CandidateSet(purpose="Choose shot")
    s.add(a)

    selected = s.select(a.id)

    assert selected.status == CandidateStatus.APPROVED
    assert s.winner() == a
