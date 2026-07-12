from __future__ import annotations

from opendirector.creative.context import CreativeContext
from opendirector.creative.program import CreativeProgram


class CreativeEngine:
    """Execute CreativePrograms over a shared CreativeContext."""

    async def run(
        self,
        program: CreativeProgram,
        context: CreativeContext,
    ) -> CreativeContext:
        context.record("program_name", program.name)
        context.record("completed_operators", [])
        context.record("completed_cycles", [])

        if program.cycles:
            for cycle in program.cycles:
                context = await cycle.run(context)

                cycle_report = context.metadata["cycle_reports"][-1]
                context.metadata["completed_cycles"].append(cycle.name)
                context.metadata["completed_operators"].extend(
                    cycle_report["completed_operators"]
                )

            return context

        # Backward-compatible direct-operator execution.
        for operator in program.operators:
            context = await operator.execute(context)
            context.metadata["completed_operators"].append(operator.name)

        return context
