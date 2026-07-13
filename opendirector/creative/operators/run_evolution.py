from __future__ import annotations

from opendirector.creative.context import CreativeContext
from opendirector.creative.operator import CreativeOperator
from opendirector.evolution import EvolutionEngine


class RunEvolutionGenerationOperator(CreativeOperator):
    """Run one complete generation through the EvolutionEngine."""

    name = "run_evolution_generation"

    def __init__(self, engine: EvolutionEngine) -> None:
        self.engine = engine

    async def execute(self, context: CreativeContext) -> CreativeContext:
        return await self.engine.run_generation(context)
