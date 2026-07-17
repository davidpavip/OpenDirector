import asyncio

from opendirector import Studio
from opendirector.applications.scene_planner import (
    build_scene_planning_context,
    build_scene_planning_program,
)
from opendirector.planning import (
    ScenePlanning,
    SceneUnderstanding,
)


def test_scene_completes_planning_circle():
    studio = Studio("Gilbert Studio")

    scene = ScenePlanning(
        id="scene-001",
        title="The Discovery",
        understanding=SceneUnderstanding(
            objective=("Introduce the boy and reveal the abandoned robot."),
            emotional_objective=("Create loneliness, curiosity, and hope."),
            story_function="Inciting incident",
            required_information=(
                "The boy is alone.",
                "The robot is inactive.",
            ),
            constraints=(
                "No dialogue.",
                "Family-friendly.",
            ),
            confidence=0.85,
        ),
    )

    result = asyncio.run(
        studio.run(
            build_scene_planning_program(),
            build_scene_planning_context(scene),
        )
    )

    assert result.scene_thinking is not None

    planned = result.scene_thinking.scene
    assert planned is not None

    assert planned.status == "planned"
    assert len(planned.ideas) == 3
    assert len(planned.critiques) == 3
    assert planned.decision is not None
    assert len(planned.shots) == 4

    assert result.metadata["completed_operators"] == [
        "imagine_scene",
        "critique_scene",
        "decide_scene",
        "plan_scene_shots",
    ]


def test_shots_are_short_rendering_units():
    studio = Studio("Gilbert Studio")

    scene = ScenePlanning(
        id="scene-002",
        title="First Activation",
        understanding=SceneUnderstanding(
            objective="Activate the robot.",
            emotional_objective="Move from fear to trust.",
            story_function="Relationship beat",
            confidence=0.8,
        ),
    )

    result = asyncio.run(
        studio.run(
            build_scene_planning_program(),
            build_scene_planning_context(scene),
        )
    )

    assert result.scene_thinking is not None
    planned = result.scene_thinking.scene
    assert planned is not None

    assert all(shot.estimated_duration_seconds <= 10 for shot in planned.shots)
