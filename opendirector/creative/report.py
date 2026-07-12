from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CycleIterationReport:
    """Record of one completed CreativeCycle iteration."""

    cycle_name: str
    iteration: int
    completed_operators: tuple[str, ...]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CycleReport:
    """Summary of an entire CreativeCycle execution."""

    cycle_name: str
    iterations: tuple[CycleIterationReport, ...]
    stop_reason: str

    @property
    def iteration_count(self) -> int:
        return len(self.iterations)

    @property
    def completed_operators(self) -> tuple[str, ...]:
        return tuple(
            operator_name
            for iteration in self.iterations
            for operator_name in iteration.completed_operators
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "cycle_name": self.cycle_name,
            "iteration_count": self.iteration_count,
            "stop_reason": self.stop_reason,
            "completed_operators": list(self.completed_operators),
            "iterations": [
                {
                    "cycle_name": iteration.cycle_name,
                    "iteration": iteration.iteration,
                    "completed_operators": list(iteration.completed_operators),
                    "metadata": dict(iteration.metadata),
                }
                for iteration in self.iterations
            ],
        }
