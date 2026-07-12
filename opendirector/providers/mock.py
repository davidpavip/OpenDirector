from __future__ import annotations

from opendirector.providers.language import LanguageRequest, LanguageResult


class MockLanguageProvider:
    """Deterministic provider used for architecture and integration tests."""

    provider_id = "mock.language"
    display_name = "Mock Language Provider"

    async def generate(self, request: LanguageRequest) -> LanguageResult:
        return LanguageResult(
            text=(
                "Candidate B is recommended because it has the strongest "
                "editorial clarity and pacing."
            ),
            model="mock-language-v1",
            provider_id=self.provider_id,
            metadata={
                "request_received": True,
                "candidate_scores": [72, 91, 83],
                "recommended_index": 1,
            },
        )
