from __future__ import annotations

from dataclasses import dataclass, field

from opendirector.planning.operator import PlanningOperator


@dataclass
class PlanningProgram:
    """Ordered planning operations that produce a blueprint."""

    name: str
    operators: list[PlanningOperator] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("PlanningProgram name cannot be empty")

    def add(self, operator: PlanningOperator) -> PlanningOperator:
        self.operators.append(operator)
        return operator
