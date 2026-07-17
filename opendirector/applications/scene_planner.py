from __future__ import annotations

from opendirector.creative import (
    CreativeContext,
    CreativeProgram,
)
from opendirector.planning import (
    CritiqueSceneOperator,
    DecideSceneOperator,
    ImagineSceneOperator,
    PlanSceneShotsOperator,
    ScenePlanning,
    SceneThinkingContext,
)


def build_scene_planning_program() -> CreativeProgram:
    return CreativeProgram(
        name="Scene Planning Circle",
        operators=[
            ImagineSceneOperator(),
            CritiqueSceneOperator(),
            DecideSceneOperator(),
            PlanSceneShotsOperator(),
        ],
    )


def build_scene_planning_context(
    scene: ScenePlanning,
) -> CreativeContext:
    return CreativeContext(
        scene_thinking=SceneThinkingContext(
            scene_id=scene.id,
            title=scene.title,
            scene=scene,
        )
    )
