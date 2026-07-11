from __future__ import annotations

from dataclasses import dataclass, field

from opendirector.creative.operator import CreativeOperator


@dataclass
class CreativeProgram:
    """An ordered sequence of creative operators."""

    name: str
    operators: list[CreativeOperator] = field(default_factory=list)

    def add(self, operator: CreativeOperator) -> CreativeOperator:
        self.operators.append(operator)
        return operator
