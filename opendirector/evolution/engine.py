from __future__ import annotations

from opendirector.core.candidate import CandidateSet
from opendirector.evolution.strategy import EvolutionStrategy, KeepBestStrategy


class EvolutionEngine:
    """Coordinate creative evolution of candidate sets."""

    def __init__(self, strategy: EvolutionStrategy | None = None):
        self.strategy = strategy or KeepBestStrategy()

    def evolve(self, candidate_set: CandidateSet) -> CandidateSet:
        return self.strategy.evolve(candidate_set)
