from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from opendirector.core.candidate import Candidate, CandidateSet
from opendirector.core.creative_traits import CreativeTraits
from opendirector.creative.context import CreativeContext
from opendirector.creative.operator import CreativeOperator


@dataclass(frozen=True)
class TraitMutation:
    """One named mutation applied to a parent's creative traits."""

    name: str
    changes: dict[str, Any] = field(default_factory=dict)


class EvolveCandidatesOperator(CreativeOperator):
    """Create a new generation from the currently selected candidate."""

    name = "evolve_candidates"

    def __init__(
        self,
        mutations: list[TraitMutation],
        preserve_parent: bool = True,
    ) -> None:
        if not mutations:
            raise ValueError("At least one trait mutation is required")

        self.mutations = list(mutations)
        self.preserve_parent = preserve_parent

    async def execute(self, context: CreativeContext) -> CreativeContext:
        current_set = context.candidate_set

        if current_set is None:
            raise ValueError("EvolveCandidatesOperator requires a CandidateSet")

        if current_set.selected_id is None:
            raise ValueError("EvolveCandidatesOperator requires a selected candidate")

        ##        parent = current_set.selected()
        ##        if parent is None:
        ##            raise ValueError("Selected candidate could not be resolved")

        parent = next(
            (
                candidate
                for candidate in current_set.candidates
                if candidate.id == current_set.selected_id
            ),
            None,
        )

        if parent is None:
            raise ValueError("Selected candidate could not be resolved")

        parent_traits = CreativeTraits.from_dict(
            parent.payload.get("creative_traits", {})
        )

        generation = int(
            parent.payload.get(
                "generation",
                context.metadata.get("generation", 1),
            )
        )
        next_generation = generation + 1

        evolved_set = CandidateSet(purpose=f"Evolved from: {current_set.purpose}")

        if self.preserve_parent:
            elite = Candidate(
                candidate_type=parent.candidate_type,
                title=f"{parent.title} — preserved",
                created_by=self.name,
                payload={
                    **parent.payload,
                    "generation": next_generation,
                    "parent_candidate_ids": [parent.id],
                    "evolution_operation": "elite_preservation",
                    "creative_traits": parent_traits.to_dict(),
                },
            )
            evolved_set.add(elite)

        for mutation in self.mutations:
            evolved_traits = parent_traits.evolve(**mutation.changes)

            child = Candidate(
                candidate_type=parent.candidate_type,
                title=f"{parent.title} — {mutation.name}",
                created_by=self.name,
                payload={
                    "generation": next_generation,
                    "parent_candidate_ids": [parent.id],
                    "evolution_operation": "mutation",
                    "mutation_name": mutation.name,
                    "creative_traits": evolved_traits.to_dict(),
                },
            )
            evolved_set.add(child)

        context.candidate_set = evolved_set
        context.record("generation", next_generation)
        context.record("evolution_parent_id", parent.id)
        context.record(
            "evolved_candidate_count",
            len(evolved_set.candidates),
        )

        context.metadata.setdefault("generation_history", []).append(
            {
                "generation": next_generation,
                "parent_candidate_id": parent.id,
                "candidate_set_id": evolved_set.id,
                "candidate_ids": [candidate.id for candidate in evolved_set.candidates],
            }
        )

        return context
