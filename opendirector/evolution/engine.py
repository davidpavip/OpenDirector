from __future__ import annotations

from opendirector.creative.context import CreativeContext
from opendirector.evolution.generation import GenerationResult
from opendirector.evolution.strategy import EvolutionStrategy


class EvolutionEngine:
    """Execute one generation of creative evolution."""

    def __init__(self, strategy: EvolutionStrategy) -> None:
        self.strategy = strategy

    async def run_generation(
        self,
        context: CreativeContext,
    ) -> CreativeContext:
        generation = int(context.metadata.get("generation", 0)) + 1
        mode = "seed" if generation == 1 else "evolve"

        context.record("generation", generation)
        context.record("generation_mode", mode)
        context.record("evolution_strategy", self.strategy.name)

        completed: list[str] = []

        operators = self.strategy.operators_for_generation(
            context,
            generation,
        )

        for operator in operators:
            context = await operator.execute(context)
            completed.append(operator.name)

        candidate_set = context.candidate_set

        if candidate_set is None:
            raise ValueError("Evolution generation completed without a CandidateSet")

        if candidate_set.selected_id is None:
            raise ValueError(
                "Evolution generation completed without a selected candidate"
            )

        result = GenerationResult(
            generation=generation,
            mode=mode,
            candidate_set_id=candidate_set.id,
            selected_candidate_id=candidate_set.selected_id,
            completed_operators=tuple(completed),
        )

        context.metadata.setdefault("generation_reports", []).append(result.to_dict())
        context.record("last_generation_report", result.to_dict())

        return context
