import asyncio

from opendirector import Studio
from opendirector.core.candidate import Candidate, CandidateSet
from opendirector.creative import (
    CreativeContext,
    CreativeCycle,
    CreativeProgram,
    MaxIterationsCondition,
)
from opendirector.creative.operator import CreativeOperator
from opendirector.creative.operators import (
    ReviewCandidatesOperator,
    SelectCandidateOperator,
)
from opendirector.crew import Editor
from opendirector.providers import MockLanguageProvider


class IterationCreateOperator(CreativeOperator):
    """Create three fresh candidates for every cycle iteration."""

    name = "create_iteration_candidates"

    async def execute(self, context: CreativeContext) -> CreativeContext:
        iteration = context.metadata["current_cycle_iteration"]

        candidate_set = CandidateSet(
            purpose=f"Choose opening shot, iteration {iteration}"
        )

        candidate_set.add(
            Candidate(
                candidate_type="shot",
                title=f"Wide sunrise v{iteration}",
                created_by=self.name,
            )
        )
        candidate_set.add(
            Candidate(
                candidate_type="shot",
                title=f"Emotional close-up v{iteration}",
                created_by=self.name,
            )
        )
        candidate_set.add(
            Candidate(
                candidate_type="shot",
                title=f"Tracking reveal v{iteration}",
                created_by=self.name,
            )
        )

        context.candidate_set = candidate_set

        context.metadata.setdefault("candidate_set_history", []).append(
            candidate_set.id
        )

        return context


def build_studio() -> Studio:
    studio = Studio("Gilbert Studio")

    provider = studio.providers.register(MockLanguageProvider())

    studio.crew.add(Editor(provider))

    return studio


def test_real_creative_cycle_runs_three_iterations():
    studio = build_studio()

    cycle = CreativeCycle(
        name="Opening Shot Evolution",
        operators=[
            IterationCreateOperator(),
            ReviewCandidatesOperator(studio.crew),
            SelectCandidateOperator(),
        ],
        stopping_condition=MaxIterationsCondition(3),
    )

    program = CreativeProgram(
        name="Opening Shot Program",
        cycles=[cycle],
    )

    result = asyncio.run(
        studio.run(
            program,
            CreativeContext(),
        )
    )

    assert result.metadata["completed_cycles"] == ["Opening Shot Evolution"]

    assert result.metadata["completed_operators"] == [
        "create_iteration_candidates",
        "review_candidates",
        "select_candidate",
        "create_iteration_candidates",
        "review_candidates",
        "select_candidate",
        "create_iteration_candidates",
        "review_candidates",
        "select_candidate",
    ]

    assert len(result.metadata["candidate_set_history"]) == 3
    assert len(set(result.metadata["candidate_set_history"])) == 3

    report = result.metadata["cycle_reports"][0]

    assert report["iteration_count"] == 3
    assert report["stop_reason"] == "maximum iterations reached: 3"

    assert [item["iteration"] for item in report["iterations"]] == [
        1,
        2,
        3,
    ]

    for iteration_report in report["iterations"]:
        assert iteration_report["completed_operators"] == [
            "create_iteration_candidates",
            "review_candidates",
            "select_candidate",
        ]
        assert iteration_report["metadata"]["candidate_set_id"] is not None
        assert iteration_report["metadata"]["selected_candidate_id"] is not None


def test_final_context_contains_final_iteration_winner():
    studio = build_studio()

    cycle = CreativeCycle(
        name="Two Iteration Evolution",
        operators=[
            IterationCreateOperator(),
            ReviewCandidatesOperator(studio.crew),
            SelectCandidateOperator(),
        ],
        stopping_condition=MaxIterationsCondition(2),
    )

    program = CreativeProgram(
        name="Final Winner Program",
        cycles=[cycle],
    )

    result = asyncio.run(
        studio.run(
            program,
            CreativeContext(),
        )
    )

    candidate_set = result.candidate_set

    assert candidate_set is not None
    assert candidate_set.selected_id is not None

    winner = candidate_set.winner()

    assert winner is not None
    assert winner.title == "Emotional close-up v2"
    assert result.metadata["selected_candidate_id"] == winner.id
    assert result.metadata["selected_candidate_title"] == winner.title
    assert result.metadata["selected_candidate_score"] == 91


def test_each_iteration_produces_reviewed_candidates():
    studio = build_studio()

    cycle = CreativeCycle(
        name="Editorial Evolution",
        operators=[
            IterationCreateOperator(),
            ReviewCandidatesOperator(studio.crew),
            SelectCandidateOperator(),
        ],
        stopping_condition=MaxIterationsCondition(2),
    )

    program = CreativeProgram(
        name="Editorial Validation",
        cycles=[cycle],
    )

    result = asyncio.run(
        studio.run(
            program,
            CreativeContext(),
        )
    )

    candidate_set = result.candidate_set
    assert candidate_set is not None

    for candidate in candidate_set.candidates:
        assert len(candidate.scores) == 1
        assert candidate.scores[0].category == "editing"
        assert candidate.scores[0].reviewer == "Studio Editor"
