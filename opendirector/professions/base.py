from __future__ import annotations

from abc import ABC, abstractmethod

from opendirector.professions.context import ProfessionContext
from opendirector.professions.models import (
    Assignment,
    Deliverable,
    PreparedAssignment,
    ProfessionResult,
    Reflection,
)


class Profession(ABC):
    """A reusable cognitive specialization of the Studio Mind.

    Lifecycle:

        prepare
        → perform
        → reflect
        → return result

    Values govern.
    Education informs.
    Experience refines.
    """

    name: str

    def __init__(self) -> None:
        if not getattr(self, "name", "").strip():
            raise ValueError("Profession name cannot be empty")

    async def invoke(
        self,
        assignment: Assignment,
        context: ProfessionContext,
    ) -> ProfessionResult:
        self._validate_assignment(assignment)

        prepared = await self.prepare(
            assignment=assignment,
            context=context,
        )

        deliverable = await self.perform(prepared)

        self._validate_deliverable(
            assignment=assignment,
            deliverable=deliverable,
        )

        reflection = await self.reflect(
            prepared=prepared,
            deliverable=deliverable,
        )

        return ProfessionResult(
            assignment=assignment,
            prepared=prepared,
            deliverable=deliverable,
            reflection=reflection,
        )

    async def prepare(
        self,
        assignment: Assignment,
        context: ProfessionContext,
    ) -> PreparedAssignment:
        """Refresh values, education, experience, and current context."""

        return PreparedAssignment(
            assignment=assignment,
            values=tuple(context.values),
            education=tuple(context.education),
            experience=tuple(context.experience),
            source_context=context.source,
            production_context=context.production,
            conversation_context=context.conversation,
        )

    @abstractmethod
    async def perform(
        self,
        prepared: PreparedAssignment,
    ) -> Deliverable:
        """Carry out the professional assignment."""

        raise NotImplementedError

    async def reflect(
        self,
        prepared: PreparedAssignment,
        deliverable: Deliverable,
    ) -> Reflection | None:
        """Evaluate completed work.

        The default profession does not manufacture lessons. Concrete
        professions may return evidence-based reflections.
        """

        del prepared, deliverable
        return None

    def _validate_assignment(
        self,
        assignment: Assignment,
    ) -> None:
        if assignment.profession.strip().lower() != self.name.lower():
            raise ValueError(
                f"Assignment is for profession "
                f"{assignment.profession!r}, not {self.name!r}"
            )

    def _validate_deliverable(
        self,
        assignment: Assignment,
        deliverable: Deliverable,
    ) -> None:
        if deliverable.assignment_id != assignment.id:
            raise ValueError("Deliverable does not belong to the current assignment")

        if deliverable.profession.strip().lower() != self.name.lower():
            raise ValueError("Deliverable profession does not match invoked profession")
