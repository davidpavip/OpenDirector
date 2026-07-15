import asyncio

from opendirector import Studio
from opendirector.creative import (
    CreativeContext,
    CreativeProgram,
)
from opendirector.planning import (
    BlueprintStatus,
    PlanningContext,
    PlanningProgram,
    SourceDocument,
)
from opendirector.planning.operators import (
    ApproveBlueprintOperator,
    DefineIntentOperator,
    DesignStoryOperator,
)


def build_planning_context() -> PlanningContext:
    return PlanningContext(
        source=SourceDocument(
            content=("# Creative Brief\n\n" "A boy discovers an abandoned robot.")
        )
    )


def test_planning_runs_through_creative_engine():
    studio = Studio("Gilbert Studio")

    program = CreativeProgram(
        name="Unified Planning",
        operators=[
            DefineIntentOperator("Create a hopeful family animation."),
            DesignStoryOperator("A boy repairs a robot and forms a friendship."),
            ApproveBlueprintOperator("Gilbert"),
        ],
    )

    result = asyncio.run(
        studio.run(
            program,
            CreativeContext(
                planning=build_planning_context(),
            ),
        )
    )

    assert result.planning is not None
    assert result.planning.blueprint is not None

    assert result.planning.blueprint.status is BlueprintStatus.APPROVED

    assert result.metadata["completed_operators"] == [
        "define_intent",
        "design_story",
        "approve_blueprint",
    ]


def test_planning_program_is_a_creative_program():
    program = PlanningProgram(
        name="Planning Alias",
        operators=[
            DefineIntentOperator("Create a short film."),
        ],
    )

    assert isinstance(program, CreativeProgram)


def test_studio_plan_remains_backward_compatible():
    studio = Studio("Gilbert Studio")

    program = PlanningProgram(
        name="Legacy Planning API",
        operators=[
            DefineIntentOperator("Create a hopeful animation."),
            DesignStoryOperator("A child discovers a forgotten machine."),
            ApproveBlueprintOperator("Gilbert"),
        ],
    )

    result = asyncio.run(
        studio.plan(
            program,
            build_planning_context(),
        )
    )

    assert result.blueprint is not None
    assert result.blueprint.is_approved

    assert result.metadata["completed_planning_operators"] == [
        "define_intent",
        "design_story",
        "approve_blueprint",
    ]
