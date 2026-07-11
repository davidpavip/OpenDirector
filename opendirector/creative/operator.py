from __future__ import annotations

from abc import ABC, abstractmethod

from opendirector.creative.context import CreativeContext


class CreativeOperator(ABC):
    """One composable operation in a creative program."""

    name: str = "operator"

    @abstractmethod
    async def execute(self, context: CreativeContext) -> CreativeContext:
        raise NotImplementedError
