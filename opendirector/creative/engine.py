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

        for operator in program.operators:
            context = await operator.execute(context)
            context.metadata["completed_operators"].append(operator.name)

        return context
