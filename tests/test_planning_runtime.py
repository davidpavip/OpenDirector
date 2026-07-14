import asyncio

import pytest

from opendirector import Studio
from opendirector.planning import (
    AssignmentMode,
    BlueprintStatus,
    PlanningContext,
    PlanningProgram,
    Profession,
    RoleAssignment,
    SourceDocument,
    StoryRole,
)
from opendirector.planning.operators import (
    ApproveBlueprintOperator,
    AssignProfessionsOperator,
    DefineIntentOperator,
    DefineProfessionsOperator,
    DefineStoryRolesOperator,
    DesignStoryOperator,
)


def test_complete_planning_program_creates_approved_blueprint():
    studio = Studio("Gilbert Studio")

    source = SourceDocument(
        title="The Little Robot",
        content="""
# Creative Brief

A lonely boy discovers an abandoned robot near a mountain village.
""",
    )

    program = PlanningProgram(
        name="Original Story Planning",
        operators=[
            DefineIntentOperator("Create a hopeful family animation about friendship."),
            DesignStoryOperator(
                "A lonely boy repairs a forgotten robot and discovers "
                "that companionship can restore hope to both of them."
            ),
            DefineStoryRolesOperator(
                [
                    StoryRole(
                        name="Boy",
                        purpose="Protagonist seeking companionship.",
                        importance="primary",
                    ),
                    StoryRole(
                        name="Robot",
                        purpose="Companion whose recovery drives the story.",
                        importance="primary",
                    ),
                ]
            ),
            DefineProfessionsOperator(
                [
                    Profession(
                        name="Director",
                        responsibilities=("Own creative intent",),
                    ),
                    Profession(
                        name="Editor",
                        responsibilities=("Review pacing",),
                    ),
                    Profession(
                        name="Composer",
                        responsibilities=("Design musical language",),
                    ),
                ]
            ),
            AssignProfessionsOperator(
                [
                    RoleAssignment(
                        profession_name="Director",
                        mode=AssignmentMode.HUMAN,
                        performer="Gilbert",
                    ),
                    RoleAssignment(
                        profession_name="Editor",
                        mode=AssignmentMode.AI_ASSISTANT,
                        performer="OpenDirector",
                    ),
                    RoleAssignment(
                        profession_name="Composer",
                        mode=AssignmentMode.AI_DELEGATE,
                        performer="OpenDirector",
                    ),
                ]
            ),
            ApproveBlueprintOperator(approved_by="Gilbert"),
        ],
    )

    result = asyncio.run(
        studio.plan(
            program,
            PlanningContext(source=source),
        )
    )

    blueprint = result.blueprint
    assert blueprint is not None

    assert blueprint.status is BlueprintStatus.APPROVED
    assert blueprint.approved_by == "Gilbert"
    assert len(blueprint.story_roles) == 2
    assert len(blueprint.professions) == 3
    assert len(blueprint.assignments) == 3

    assert result.metadata["completed_planning_operators"] == [
        "define_intent",
        "design_story",
        "define_story_roles",
        "define_professions",
        "assign_professions",
        "approve_blueprint",
    ]


def test_blueprint_cannot_be_approved_without_intent():
    studio = Studio("Gilbert Studio")

    program = PlanningProgram(
        name="Invalid Planning",
        operators=[
            DesignStoryOperator("A complete story."),
            ApproveBlueprintOperator("Gilbert"),
        ],
    )

    with pytest.raises(ValueError, match="requires an intent"):
        asyncio.run(
            studio.plan(
                program,
                PlanningContext(source=SourceDocument(content="Story source")),
            )
        )


def test_assignment_requires_defined_profession():
    studio = Studio("Gilbert Studio")

    program = PlanningProgram(
        name="Invalid Assignment",
        operators=[
            DefineProfessionsOperator([Profession(name="Director")]),
            AssignProfessionsOperator(
                [
                    RoleAssignment(
                        profession_name="Composer",
                        mode=AssignmentMode.AI_ASSISTANT,
                    )
                ]
            ),
        ],
    )

    with pytest.raises(
        ValueError,
        match="undefined professions",
    ):
        asyncio.run(
            studio.plan(
                program,
                PlanningContext(source=SourceDocument(content="Story source")),
            )
        )


def test_approved_blueprint_can_be_revised_as_new_version():
    source = SourceDocument(content="A short creative brief.")

    context = PlanningContext(source=source)
    assert context.blueprint is not None

    from dataclasses import replace

    draft = replace(
        context.blueprint,
        intent_summary="Create a short film.",
        story_summary="A complete story.",
    )

    approved = draft.approve("Gilbert")
    revised = approved.revise()

    assert approved.version == 1
    assert approved.is_approved

    assert revised.version == 2
    assert not revised.is_approved
    assert revised.approved_by is None
