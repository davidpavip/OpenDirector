from __future__ import annotations

from dataclasses import replace

from opendirector.core.candidate import Candidate, CandidateSet
from opendirector.creative.context import CreativeContext
from opendirector.creative.operator import CreativeOperator
from opendirector.planning.evolution import (
    BlueprintMutation,
    BlueprintSeed,
)
from opendirector.planning.models import ProductionBlueprint

BLUEPRINT_PAYLOAD_KEY = "production_blueprint"


def blueprint_from_candidate(
    candidate: Candidate,
) -> ProductionBlueprint:
    blueprint = candidate.payload.get(BLUEPRINT_PAYLOAD_KEY)

    if not isinstance(blueprint, ProductionBlueprint):
        raise ValueError("Candidate does not contain a ProductionBlueprint")

    return blueprint


class SeedBlueprintsOperator(CreativeOperator):
    """Create the first population of blueprint interpretations."""

    name = "seed_blueprints"

    def __init__(
        self,
        template: ProductionBlueprint,
        seeds: list[BlueprintSeed],
    ) -> None:
        if not seeds:
            raise ValueError("At least one blueprint seed is required")

        self.template = template
        self.seeds = tuple(seeds)

    async def execute(
        self,
        context: CreativeContext,
    ) -> CreativeContext:
        candidate_set = CandidateSet(purpose="Select a production blueprint")

        for seed in self.seeds:
            blueprint = seed.create_blueprint(self.template)

            candidate_set.add(
                Candidate(
                    candidate_type="production_blueprint",
                    title=seed.title,
                    created_by=self.name,
                    payload={
                        BLUEPRINT_PAYLOAD_KEY: blueprint,
                        "generation": 1,
                        "evolution_operation": "seed",
                    },
                )
            )

        context.candidate_set = candidate_set
        context.record("generation", 1)
        context.record(
            "blueprint_candidate_count",
            len(candidate_set.candidates),
        )

        return context


class EvolveBlueprintsOperator(CreativeOperator):
    """Create a new blueprint population from the selected parent."""

    name = "evolve_blueprints"

    def __init__(
        self,
        mutations: list[BlueprintMutation],
        preserve_parent: bool = True,
    ) -> None:
        if not mutations:
            raise ValueError("At least one blueprint mutation is required")

        self.mutations = tuple(mutations)
        self.preserve_parent = preserve_parent

    async def execute(
        self,
        context: CreativeContext,
    ) -> CreativeContext:
        current_set = context.candidate_set

        if current_set is None:
            raise ValueError("EvolveBlueprintsOperator requires a CandidateSet")

        if current_set.selected_id is None:
            raise ValueError("EvolveBlueprintsOperator requires a selected blueprint")

        parent_candidate = next(
            (
                candidate
                for candidate in current_set.candidates
                if candidate.id == current_set.selected_id
            ),
            None,
        )

        if parent_candidate is None:
            raise ValueError("Selected blueprint candidate could not be resolved")

        parent_blueprint = blueprint_from_candidate(parent_candidate)

        ##        current_generation = int(
        ##            context.metadata.get(
        ##                "generation",
        ##                parent_candidate.payload.get("generation", 1),
        ##            )
        ##        )
        ##        next_generation = current_generation + 1

        # EvolutionEngine owns generation advancement.
        next_generation = int(context.metadata.get("generation", 2))

        evolved_set = CandidateSet(purpose="Evolve the selected production blueprint")

        if self.preserve_parent:
            elite_blueprint = replace(
                parent_blueprint,
                metadata={
                    **parent_blueprint.metadata,
                    "blueprint_candidate_title": (
                        f"{parent_candidate.title} — preserved"
                    ),
                    "evolution_operation": "elite_preservation",
                    "generation": next_generation,
                    "parent_candidate_id": parent_candidate.id,
                },
            )

            evolved_set.add(
                Candidate(
                    candidate_type="production_blueprint",
                    title=f"{parent_candidate.title} — preserved",
                    created_by=self.name,
                    payload={
                        BLUEPRINT_PAYLOAD_KEY: elite_blueprint,
                        "generation": next_generation,
                        "parent_candidate_ids": [parent_candidate.id],
                        "evolution_operation": ("elite_preservation"),
                    },
                )
            )

        for mutation in self.mutations:
            child_blueprint = mutation.apply(
                parent_blueprint,
                generation=next_generation,
            )

            child_candidate = Candidate(
                candidate_type="production_blueprint",
                title=mutation.name,
                created_by=self.name,
                payload={
                    BLUEPRINT_PAYLOAD_KEY: child_blueprint,
                    "generation": next_generation,
                    "parent_candidate_ids": [parent_candidate.id],
                    "evolution_operation": "mutation",
                    "mutation_name": mutation.name,
                },
            )
            evolved_set.add(child_candidate)

        context.candidate_set = evolved_set
        #        context.record("generation", next_generation)
        context.record(
            "blueprint_evolution_parent_id",
            parent_candidate.id,
        )
        context.record(
            "blueprint_candidate_count",
            len(evolved_set.candidates),
        )

        context.metadata.setdefault(
            "blueprint_generation_history",
            [],
        ).append(
            {
                "generation": next_generation,
                "parent_candidate_id": parent_candidate.id,
                "candidate_set_id": evolved_set.id,
                "candidate_ids": [candidate.id for candidate in evolved_set.candidates],
            }
        )

        return context


class ExtractSelectedBlueprintOperator(CreativeOperator):
    """Expose the selected blueprint after evolution."""

    name = "extract_selected_blueprint"

    async def execute(
        self,
        context: CreativeContext,
    ) -> CreativeContext:
        candidate_set = context.candidate_set

        if candidate_set is None:
            raise ValueError(
                "ExtractSelectedBlueprintOperator requires " "a CandidateSet"
            )

        if candidate_set.selected_id is None:
            raise ValueError("No blueprint candidate has been selected")

        selected = next(
            (
                candidate
                for candidate in candidate_set.candidates
                if candidate.id == candidate_set.selected_id
            ),
            None,
        )

        if selected is None:
            raise ValueError("Selected blueprint candidate could not be resolved")

        blueprint = blueprint_from_candidate(selected)

        context.record("selected_blueprint", blueprint)
        context.record(
            "selected_blueprint_candidate_id",
            selected.id,
        )
        context.record(
            "selected_blueprint_title",
            selected.title,
        )

        return context
