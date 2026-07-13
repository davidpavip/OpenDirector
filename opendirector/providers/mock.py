from __future__ import annotations

import re

from opendirector.providers.language import LanguageRequest, LanguageResult


class MockLanguageProvider:
    """Deterministic language provider for tests and local development."""

    provider_id = "mock.language"
    display_name = "Mock Language Provider"

    async def generate(self, request: LanguageRequest) -> LanguageResult:
        candidate_count = self._candidate_count(request)
        scores = self._build_scores(candidate_count)

        recommended_index = (
            max(range(len(scores)), key=scores.__getitem__) if scores else None
        )

        return LanguageResult(
            text=self._build_recommendation(
                recommended_index=recommended_index,
                scores=scores,
            ),
            model="mock-language-v1",
            provider_id=self.provider_id,
            metadata={
                "request_received": True,
                "candidate_scores": scores,
                "recommended_index": recommended_index,
            },
        )

    def _candidate_count(self, request: LanguageRequest) -> int:
        explicit_count = request.metadata.get("candidate_count")

        if explicit_count is not None:
            count = int(explicit_count)
            if count < 0:
                raise ValueError("candidate_count cannot be negative")
            return count

        # Backward compatibility for tests or callers that describe
        # candidates only in the user message.
        matches = re.findall(
            r"\bCandidate\s+[A-Z0-9]+\b",
            request.user_message,
            flags=re.IGNORECASE,
        )
        return len(matches)

    def _build_scores(self, candidate_count: int) -> list[int]:
        preferred_scores = [72, 91, 83, 76, 68]

        if candidate_count <= len(preferred_scores):
            return preferred_scores[:candidate_count]

        scores = list(preferred_scores)

        while len(scores) < candidate_count:
            scores.append(max(50, scores[-1] - 3))

        return scores

    def _build_recommendation(
        self,
        recommended_index: int | None,
        scores: list[int],
    ) -> str:
        if recommended_index is None:
            return "No candidates were available for review."

        candidate_label = self._candidate_label(recommended_index)

        return (
            f"Candidate {candidate_label} is recommended because it has "
            f"the strongest editorial score ({scores[recommended_index]})."
        )

    def _candidate_label(self, index: int) -> str:
        """Convert zero-based indexes to A, B, ..., Z, AA, AB, ..."""

        label = ""
        value = index + 1

        while value:
            value, remainder = divmod(value - 1, 26)
            label = chr(65 + remainder) + label

        return label
