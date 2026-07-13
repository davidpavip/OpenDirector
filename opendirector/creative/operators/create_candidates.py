from __future__ import annotations

from dataclasses import dataclass

from opendirector.core.candidate import Candidate, CandidateSet
from opendirector.creative.context import CreativeContext
from opendirector.creative.operator import CreativeOperator
from opendirector.core.creative_traits import CreativeTraits


@dataclass(frozen=True)
class CandidateBlueprint:
    title: str
    candidate_type: str = "shot"


class CreateCandidatesOperator(CreativeOperator):
    """Create deterministic candidates for the current creative context.

    This first implementation proves the workflow without using an AI provider.
    Later, a Director or Writer crew member can generate the blueprints.
    """

    name = "create_candidates"

    def __init__(
        self,
        purpose: str,
        blueprints: list[CandidateBlueprint],
        created_by: str = "creative.create",
    ) -> None:
        if not purpose.strip():
            raise ValueError("CandidateSet purpose cannot be empty")

        if not blueprints:
            raise ValueError("At least one candidate blueprint is required")

        self.purpose = purpose
        self.blueprints = list(blueprints)
        self.created_by = created_by

    async def execute(self, context: CreativeContext) -> CreativeContext:
        candidate_set = CandidateSet(purpose=self.purpose)

        for blueprint in self.blueprints:
            candidate_set.add(
                Candidate(
                    candidate_type=blueprint.candidate_type,
                    title=blueprint.title,
                    created_by=self.created_by,
                    #                    payload={
                    #                        "source_operator": self.name,
                    #                   },
                    payload={
                        "source_operator": self.name,
                        "generation": 1,
                        "creative_traits": dict(
                            context.metadata.get(
                                "seed_creative_traits",
                                CreativeTraits().to_dict(),
                            )
                        ),
                    },
                )
            )

        context.candidate_set = candidate_set
        context.record("created_candidate_count", len(candidate_set.candidates))
        context.record("candidate_set_id", candidate_set.id)

        return context
