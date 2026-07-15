from __future__ import annotations

from abc import abstractmethod

from opendirector.creative.context import CreativeContext
from opendirector.creative.operator import CreativeOperator
from opendirector.planning.context import PlanningContext


class PlanningCreativeOperator(CreativeOperator):
    """Planning operation executed by the central CreativeEngine.

    Subclasses implement execute_planning(). This adapter keeps planning
    domain logic typed while using the universal creative runtime.
    """

    @abstractmethod
    async def execute_planning(
        self,
        context: PlanningContext,
    ) -> PlanningContext:
        raise NotImplementedError

    async def execute(
        self,
        context: CreativeContext,
    ) -> CreativeContext:
        planning_context = context.planning

        if planning_context is None:
            raise ValueError(
                f"{self.__class__.__name__} requires " "CreativeContext.planning"
            )

        context.planning = await self.execute_planning(planning_context)
        return context
