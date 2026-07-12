from __future__ import annotations

from opendirector.creative.context import CreativeContext
from opendirector.creative.operator import CreativeOperator


class SelectCandidateOperator(CreativeOperator):
    """Select the highest-scoring candidate after review."""

    name = "select_candidate"

    async def execute(self, context: CreativeContext) -> CreativeContext:
        candidate_set = context.candidate_set

        if candidate_set is None:
            raise ValueError(
                "SelectCandidateOperator requires a CandidateSet in CreativeContext"
            )

        if not candidate_set.candidates:
            raise ValueError("SelectCandidateOperator requires at least one Candidate")

        candidates_without_scores = [
            candidate.title
            for candidate in candidate_set.candidates
            if not candidate.scores
        ]

        if candidates_without_scores:
            titles = ", ".join(candidates_without_scores)
            raise ValueError(
                f"All candidates must be reviewed before selection: {titles}"
            )

        winner = candidate_set.winner()
        assert winner is not None

        selected = candidate_set.select(winner.id)

        context.record("selected_candidate_id", selected.id)
        context.record("selected_candidate_title", selected.title)
        context.record("selected_candidate_score", selected.average_score)

        return context
