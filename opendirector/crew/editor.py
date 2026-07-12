from __future__ import annotations

from opendirector.core.candidate import ReviewerScore
from opendirector.creative.context import CreativeContext
from opendirector.crew.member import CrewMember
from opendirector.providers.language import LanguageProvider, LanguageRequest


class Editor(CrewMember):
    """Editorial crew role backed by a replaceable language provider."""

    role = "editor"
    name = "Studio Editor"

    def __init__(self, provider: LanguageProvider) -> None:
        self.provider = provider

    async def perform(self, context: CreativeContext) -> CreativeContext:
        candidate_set = context.candidate_set

        if candidate_set is None:
            raise ValueError("Editor requires a CandidateSet in CreativeContext")

        if not candidate_set.candidates:
            raise ValueError("Editor requires at least one Candidate")

        request = LanguageRequest(
            system_instruction=(
                "You are a professional film editor. Review candidates for "
                "pacing, continuity, emotional impact, and clarity."
            ),
            user_message=self._build_candidate_summary(context),
            metadata={
                "candidate_set_id": candidate_set.id,
                "candidate_count": len(candidate_set.candidates),
            },
        )

        result = await self.provider.generate(request)
        raw_scores = result.metadata.get("candidate_scores", [])

        if len(raw_scores) != len(candidate_set.candidates):
            raise ValueError(
                "Provider returned a score count that does not match candidates"
            )

        for candidate, score in zip(candidate_set.candidates, raw_scores):
            candidate.add_score(
                ReviewerScore(
                    reviewer=self.name,
                    category="editing",
                    score=int(score),
                    confidence=1.0,
                    comment=result.text,
                )
            )

        context.record("reviewed_by", self.role)
        context.record("review_provider", result.provider_id)
        context.record("review_model", result.model)
        context.record("review_recommendation", result.text)
        context.record(
            "reviewed_candidate_count",
            len(candidate_set.candidates),
        )
        return context

    def _build_candidate_summary(self, context: CreativeContext) -> str:
        candidate_set = context.candidate_set
        assert candidate_set is not None

        lines = [f"Purpose: {candidate_set.purpose}"]

        if context.intent is not None:
            lines.append(f"Intent: {context.intent.message}")

        for index, candidate in enumerate(candidate_set.candidates, start=1):
            lines.append(
                f"Candidate {index}: {candidate.title}; "
                f"type={candidate.candidate_type}"
            )

        return "\n".join(lines)
