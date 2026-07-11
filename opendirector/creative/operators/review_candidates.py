from __future__ import annotations

from opendirector.creative.context import CreativeContext
from opendirector.creative.operator import CreativeOperator
from opendirector.crew import Crew


class ReviewCandidatesOperator(CreativeOperator):
    """Ask the Studio Editor to review the current CandidateSet."""

    name = "review_candidates"

    def __init__(self, crew: Crew) -> None:
        self.crew = crew

    async def execute(self, context: CreativeContext) -> CreativeContext:
        editor = self.crew.get("editor")
        return await editor.perform(context)
