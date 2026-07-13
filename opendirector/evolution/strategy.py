from __future__ import annotations

from abc import ABC, abstractmethod

from opendirector.creative.context import CreativeContext
from opendirector.creative.operator import CreativeOperator


class EvolutionStrategy(ABC):
    """Choose the operators used for one evolutionary generation."""

    name: str = "base"

    @abstractmethod
    def operators_for_generation(
        self,
        context: CreativeContext,
        generation: int,
    ) -> tuple[CreativeOperator, ...]:
        raise NotImplementedError


class SeedThenEvolveStrategy(EvolutionStrategy):
    """Seed generation one, then evolve all later generations."""

    name = "seed_then_evolve"

    def __init__(
        self,
        seed_operator: CreativeOperator,
        evolve_operator: CreativeOperator,
        review_operator: CreativeOperator,
        select_operator: CreativeOperator,
    ) -> None:
        self.seed_operator = seed_operator
        self.evolve_operator = evolve_operator
        self.review_operator = review_operator
        self.select_operator = select_operator

    def operators_for_generation(
        self,
        context: CreativeContext,
        generation: int,
    ) -> tuple[CreativeOperator, ...]:
        del context

        first_operator = self.seed_operator if generation == 1 else self.evolve_operator

        return (
            first_operator,
            self.review_operator,
            self.select_operator,
        )
