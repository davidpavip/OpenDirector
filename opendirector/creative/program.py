from __future__ import annotations

from dataclasses import dataclass, field

from opendirector.creative.cycle import CreativeCycle
from opendirector.creative.operator import CreativeOperator


@dataclass
class CreativeProgram:
    """A creative workflow composed of cycles.

    Direct operators remain supported temporarily for backward compatibility.
    """

    name: str
    cycles: list[CreativeCycle] = field(default_factory=list)
    operators: list[CreativeOperator] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("CreativeProgram name cannot be empty")

        if self.cycles and self.operators:
            raise ValueError(
                "CreativeProgram cannot define both cycles and direct operators"
            )

    def add_cycle(self, cycle: CreativeCycle) -> CreativeCycle:
        if self.operators:
            raise ValueError("Cannot add a cycle to a program using direct operators")

        self.cycles.append(cycle)
        return cycle

    def add(self, operator: CreativeOperator) -> CreativeOperator:
        """Backward-compatible direct operator API."""
        if self.cycles:
            raise ValueError("Cannot add a direct operator to a program using cycles")

        self.operators.append(operator)
        return operator
