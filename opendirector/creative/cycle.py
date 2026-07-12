from __future__ import annotations

from dataclasses import dataclass, field

from opendirector.creative.context import CreativeContext
from opendirector.creative.operator import CreativeOperator


@dataclass
class CreativeCycle:
    """One named iteration of creative work.

    A cycle groups related operators such as:

        create -> review -> select

    Later, cycles may support repeated iterations and stopping conditions.
    """

    name: str
    operators: list[CreativeOperator] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("CreativeCycle name cannot be empty")

    def add(self, operator: CreativeOperator) -> CreativeOperator:
        self.operators.append(operator)
        return operator

    async def run(self, context: CreativeContext) -> CreativeContext:
        completed: list[str] = []

        for operator in self.operators:
            context = await operator.execute(context)
            completed.append(operator.name)

        cycle_reports = context.metadata.setdefault("cycle_reports", [])
        cycle_reports.append(
            {
                "cycle_name": self.name,
                "completed_operators": completed,
            }
        )

        return context
