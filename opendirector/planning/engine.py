from __future__ import annotations

from opendirector.creative import (
    CreativeContext,
    CreativeEngine,
)
from opendirector.planning.context import PlanningContext
from opendirector.planning.program import PlanningProgram


class PlanningEngine:
    """Compatibility wrapper around the central CreativeEngine.

    Deprecated: use Studio.run() with CreativeContext(planning=...).
    """

    def __init__(self) -> None:
        self._creative_engine = CreativeEngine()

    async def run(
        self,
        program: PlanningProgram,
        context: PlanningContext,
    ) -> PlanningContext:
        creative_context = CreativeContext(
            planning=context,
        )

        result = await self._creative_engine.run(
            program,
            creative_context,
        )

        if result.planning is None:
            raise RuntimeError("Planning program completed without PlanningContext")

        # Preserve the old planning metadata contract temporarily.
        result.planning.metadata["planning_program"] = program.name

        result.planning.metadata["completed_planning_operators"] = list(
            result.metadata.get(
                "completed_operators",
                [],
            )
        )

        return result.planning
