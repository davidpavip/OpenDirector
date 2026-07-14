from __future__ import annotations

from abc import ABC, abstractmethod

from opendirector.planning.context import PlanningContext


class PlanningOperator(ABC):
    """One deterministic planning operation."""

    name: str

    @abstractmethod
    async def execute(
        self,
        context: PlanningContext,
    ) -> PlanningContext:
        raise NotImplementedError
