from __future__ import annotations

from opendirector.core.candidate import ReviewerScore
from opendirector.creative.context import CreativeContext
from opendirector.crew.member import CrewMember


class Editor(CrewMember):
    """Deterministic first implementation of the Editor role.

    This implementation proves the crew architecture without depending
    on an AI provider. It can later be replaced by an AI-backed Editor.
    """

    role = "editor"
    name = "Studio Editor"

    async def perform(self, context: CreativeContext) -> CreativeContext:
        candidate_set = context.candidate_set

        if candidate_set is None:
            raise ValueError("Editor requires a CandidateSet in CreativeContext")

        for candidate in candidate_set.candidates:
            score = min(100, 50 + len(candidate.title))

            candidate.add_score(
                ReviewerScore(
                    reviewer=self.name,
                    category="editing",
                    score=score,
                    confidence=1.0,
                    comment="Deterministic development review.",
                )
            )

        context.record("reviewed_by", self.role)
        context.record("reviewed_candidate_count", len(candidate_set.candidates))
        return context
