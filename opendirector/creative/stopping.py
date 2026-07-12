from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from opendirector.creative.context import CreativeContext
from opendirector.creative.report import CycleIterationReport


@dataclass(frozen=True)
class StopDecision:
    should_stop: bool
    reason: str = ""


class StoppingCondition(ABC):
    """Decide whether a CreativeCycle should stop after an iteration."""

    @abstractmethod
    async def evaluate(
        self,
        context: CreativeContext,
        report: CycleIterationReport,
    ) -> StopDecision:
        raise NotImplementedError


@dataclass(frozen=True)
class MaxIterationsCondition(StoppingCondition):
    """Stop after a fixed number of completed iterations."""

    max_iterations: int = 1

    def __post_init__(self) -> None:
        if self.max_iterations < 1:
            raise ValueError("max_iterations must be >= 1")

    async def evaluate(
        self,
        context: CreativeContext,
        report: CycleIterationReport,
    ) -> StopDecision:
        del context

        if report.iteration >= self.max_iterations:
            return StopDecision(
                should_stop=True,
                reason=f"maximum iterations reached: {self.max_iterations}",
            )

        return StopDecision(should_stop=False)


@dataclass(frozen=True)
class MetadataEqualsCondition(StoppingCondition):
    """Stop when a CreativeContext metadata value reaches an expected value."""

    key: str
    expected: object

    def __post_init__(self) -> None:
        if not self.key.strip():
            raise ValueError("metadata key cannot be empty")

    async def evaluate(
        self,
        context: CreativeContext,
        report: CycleIterationReport,
    ) -> StopDecision:
        del report

        actual = context.metadata.get(self.key)

        if actual == self.expected:
            return StopDecision(
                should_stop=True,
                reason=(
                    f"metadata condition satisfied: " f"{self.key} == {self.expected!r}"
                ),
            )

        return StopDecision(should_stop=False)
