from __future__ import annotations

from opendirector.creative import CreativeContext
from opendirector.creative.operator import CreativeOperator
from opendirector.thinking.understanding import (
    DeterministicUnderstandingPolicy,
    UnderstandingPolicy,
)


class UnderstandOperator(CreativeOperator):
    """Produce an explicit Understanding before creative work."""

    name = "understand"

    def __init__(
        self,
        policy: UnderstandingPolicy | None = None,
        readiness_threshold: float = 0.7,
    ) -> None:
        if not 0.0 <= readiness_threshold <= 1.0:
            raise ValueError("Readiness threshold must be between 0 and 1")

        self.policy = policy or DeterministicUnderstandingPolicy()
        self.readiness_threshold = readiness_threshold

    async def execute(
        self,
        context: CreativeContext,
    ) -> CreativeContext:
        thinking = context.thinking

        if thinking is None:
            raise ValueError("UnderstandOperator requires " "CreativeContext.thinking")

        understanding = await self.policy.understand(
            assignment=thinking.assignment,
            context=thinking.profession_context,
        )

        thinking.understanding = understanding
        thinking.record(
            "understanding_id",
            understanding.id,
        )
        thinking.record(
            "understanding_confidence",
            understanding.confidence,
        )
        thinking.record(
            "understanding_ready",
            understanding.is_ready(self.readiness_threshold),
        )

        context.record(
            "understanding",
            understanding,
        )
        context.record(
            "understanding_ready",
            understanding.is_ready(self.readiness_threshold),
        )

        return context
