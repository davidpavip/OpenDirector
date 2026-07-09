from __future__ import annotations

from abc import ABC, abstractmethod

from opendirector.core.candidate import Candidate, CandidateSet


class EvolutionStrategy(ABC):
    """Strategy for turning one generation of candidates into the next."""

    name: str = "base"

    @abstractmethod
    def evolve(self, candidate_set: CandidateSet) -> CandidateSet:
        raise NotImplementedError


class KeepBestStrategy(EvolutionStrategy):
    """Minimal first strategy: preserve the best candidate as the winner."""

    name = "keep_best"

    def evolve(self, candidate_set: CandidateSet) -> CandidateSet:
        winner = candidate_set.winner()
        evolved = CandidateSet(purpose=f"Evolved from: {candidate_set.purpose}")

        if winner is None:
            return evolved

        child = Candidate(
            candidate_type=winner.candidate_type,
            title=f"{winner.title} - evolved",
            payload={
                **winner.payload,
                "parent_candidate_id": winner.id,
                "evolution_strategy": self.name,
            },
            created_by=f"evolution:{self.name}",
        )

        evolved.add(child)
        evolved.select(child.id)
        return evolved
