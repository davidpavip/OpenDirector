import asyncio

import pytest

from opendirector import Studio
from opendirector.professions import (
    Assignment,
    Deliverable,
    Profession,
    ProfessionContext,
    ProfessionRegistry,
    Reflection,
)


class RecordingProfession(Profession):
    name = "Planner"

    async def perform(
        self,
        prepared,
    ) -> Deliverable:
        return Deliverable(
            assignment_id=prepared.assignment.id,
            profession=self.name,
            deliverable_type="planning_notes",
            content={
                "objective": prepared.objective,
                "values": list(prepared.values),
                "education": list(prepared.education),
                "experience": list(prepared.experience),
            },
        )

    async def reflect(
        self,
        prepared,
        deliverable,
    ) -> Reflection:
        del deliverable

        return Reflection(
            assignment_id=prepared.assignment.id,
            profession=self.name,
            summary="The planning assignment completed successfully.",
            lessons=("Planning should begin from filmmaker values.",),
            confidence=0.8,
        )


def test_profession_invocation_uses_preparation_lifecycle():
    planner = RecordingProfession()

    assignment = Assignment(
        profession="Planner",
        objective="Create three blueprint candidates.",
        deliverable_type="BlueprintSeed[]",
    )

    context = ProfessionContext(
        values=(
            "Human creative ownership",
            "Do not glorify violence",
        ),
        education=("Use the smallest effective cast",),
        experience=("Quiet openings worked well in the previous production",),
        source="# Creative Brief\n\nA boy finds a robot.",
    )

    result = asyncio.run(
        planner.invoke(
            assignment=assignment,
            context=context,
        )
    )

    assert result.completed
    assert result.prepared.values == context.values
    assert result.prepared.education == context.education
    assert result.prepared.experience == context.experience

    assert result.deliverable.content["objective"] == (
        "Create three blueprint candidates."
    )

    assert result.reflection is not None
    assert result.reflection.confidence == 0.8


def test_values_are_prepared_before_other_knowledge():
    planner = RecordingProfession()

    result = asyncio.run(
        planner.invoke(
            Assignment(
                profession="Planner",
                objective="Plan a short animation.",
            ),
            ProfessionContext(
                values=("Protect human intent",),
                education=("Three-act structure",),
                experience=("Minimal dialogue worked previously",),
            ),
        )
    )

    assert result.prepared.values == ("Protect human intent",)
    assert result.prepared.education == ("Three-act structure",)
    assert result.prepared.experience == ("Minimal dialogue worked previously",)


def test_profession_rejects_assignment_for_another_role():
    planner = RecordingProfession()

    with pytest.raises(
        ValueError,
        match="not 'Planner'",
    ):
        asyncio.run(
            planner.invoke(
                Assignment(
                    profession="Editor",
                    objective="Review pacing.",
                ),
                ProfessionContext(),
            )
        )


def test_registry_registers_and_resolves_profession():
    registry = ProfessionRegistry()
    planner = registry.register(RecordingProfession())

    assert len(registry) == 1
    assert registry.contains("planner")
    assert registry.get("PLANNER") is planner


def test_registry_rejects_duplicate_profession():
    registry = ProfessionRegistry()
    registry.register(RecordingProfession())

    with pytest.raises(
        ValueError,
        match="already registered",
    ):
        registry.register(RecordingProfession())


def test_studio_owns_profession_registry():
    studio = Studio("Gilbert Studio")
    planner = studio.register_profession(RecordingProfession())

    assert studio.professions.get("Planner") is planner
