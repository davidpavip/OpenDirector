from __future__ import annotations

from opendirector.planning.context import PlanningContext
from opendirector.planning.program import PlanningProgram


class PlanningEngine:
    """Execute planning programs over a shared PlanningContext."""

    async def run(
        self,
        program: PlanningProgram,
        context: PlanningContext,
    ) -> PlanningContext:
        context.record("planning_program", program.name)
        context.record("completed_planning_operators", [])

        for operator in program.operators:
            context = await operator.execute(context)
            context.metadata["completed_planning_operators"].append(operator.name)

        return context
