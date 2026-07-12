from __future__ import annotations

from dataclasses import dataclass, field

from opendirector.creative.context import CreativeContext
from opendirector.creative.operator import CreativeOperator
from opendirector.creative.report import (
    CycleIterationReport,
    CycleReport,
)
from opendirector.creative.stopping import (
    MaxIterationsCondition,
    StoppingCondition,
)


@dataclass
class CreativeCycle:
    """A repeatable group of creative operators.

    Each iteration executes every operator in order. After the iteration,
    the stopping condition decides whether the cycle should stop or repeat.
    """

    name: str
    operators: list[CreativeOperator] = field(default_factory=list)
    stopping_condition: StoppingCondition = field(
        default_factory=MaxIterationsCondition
    )
    safety_limit: int = 100

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("CreativeCycle name cannot be empty")

        if self.safety_limit < 1:
            raise ValueError("CreativeCycle safety_limit must be >= 1")

    def add(self, operator: CreativeOperator) -> CreativeOperator:
        self.operators.append(operator)
        return operator

    async def run(self, context: CreativeContext) -> CreativeContext:
        iteration_reports: list[CycleIterationReport] = []
        stop_reason = ""

        for iteration in range(1, self.safety_limit + 1):
            completed: list[str] = []

            context.record("current_cycle", self.name)
            context.record("current_cycle_iteration", iteration)

            for operator in self.operators:
                context = await operator.execute(context)
                completed.append(operator.name)

            iteration_report = CycleIterationReport(
                cycle_name=self.name,
                iteration=iteration,
                completed_operators=tuple(completed),
                metadata={
                    "candidate_set_id": (
                        context.candidate_set.id
                        if context.candidate_set is not None
                        else None
                    ),
                    "selected_candidate_id": context.metadata.get(
                        "selected_candidate_id"
                    ),
                },
            )
            iteration_reports.append(iteration_report)

            decision = await self.stopping_condition.evaluate(
                context,
                iteration_report,
            )

            if decision.should_stop:
                stop_reason = decision.reason or "stopping condition satisfied"
                break
        else:
            stop_reason = f"cycle safety limit reached: {self.safety_limit}"

        report = CycleReport(
            cycle_name=self.name,
            iterations=tuple(iteration_reports),
            stop_reason=stop_reason,
        )

        context.metadata.setdefault("cycle_reports", []).append(report.to_dict())
        context.record("last_cycle_report", report.to_dict())

        return context
