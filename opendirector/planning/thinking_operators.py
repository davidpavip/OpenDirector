from __future__ import annotations

from dataclasses import replace

from opendirector.creative import CreativeContext
from opendirector.creative.operator import CreativeOperator
from opendirector.planning.thinking import (
    CritiquePolicy,
    DecisionPolicy,
    DeterministicCritiquePolicy,
    DeterministicDecisionPolicy,
    DeterministicImaginePolicy,
    DeterministicShotPlanningPolicy,
    ImaginePolicy,
    ShotPlanningPolicy,
)


def require_scene(context: CreativeContext):
    thinking = context.scene_thinking

    if thinking is None:
        raise ValueError("Scene planning requires CreativeContext.scene_thinking")

    if thinking.scene is None:
        raise ValueError("Scene planning requires a ScenePlanning object")

    return thinking, thinking.scene


class ImagineSceneOperator(CreativeOperator):
    name = "imagine_scene"

    def __init__(
        self,
        policy: ImaginePolicy | None = None,
    ) -> None:
        self.policy = policy or DeterministicImaginePolicy()

    async def execute(
        self,
        context: CreativeContext,
    ) -> CreativeContext:
        thinking, scene = require_scene(context)

        ideas = await self.policy.imagine(scene, thinking)

        thinking.scene = replace(
            scene,
            ideas=ideas,
            status="ideas",
        )
        thinking.record("idea_count", len(ideas))

        return context


class CritiqueSceneOperator(CreativeOperator):
    name = "critique_scene"

    def __init__(
        self,
        policy: CritiquePolicy | None = None,
    ) -> None:
        self.policy = policy or DeterministicCritiquePolicy()

    async def execute(
        self,
        context: CreativeContext,
    ) -> CreativeContext:
        thinking, scene = require_scene(context)

        critiques = await self.policy.critique(scene, thinking)

        thinking.scene = replace(
            scene,
            critiques=critiques,
            status="critique",
        )
        thinking.record(
            "critique_count",
            len(critiques),
        )

        return context


class DecideSceneOperator(CreativeOperator):
    name = "decide_scene"

    def __init__(
        self,
        policy: DecisionPolicy | None = None,
    ) -> None:
        self.policy = policy or DeterministicDecisionPolicy()

    async def execute(
        self,
        context: CreativeContext,
    ) -> CreativeContext:
        thinking, scene = require_scene(context)

        decision = await self.policy.decide(scene, thinking)

        thinking.scene = replace(
            scene,
            decision=decision,
            status="decided",
        )
        thinking.record(
            "selected_idea_ids",
            decision.selected_idea_ids,
        )

        return context


class PlanSceneShotsOperator(CreativeOperator):
    name = "plan_scene_shots"

    def __init__(
        self,
        policy: ShotPlanningPolicy | None = None,
    ) -> None:
        self.policy = policy or DeterministicShotPlanningPolicy()

    async def execute(
        self,
        context: CreativeContext,
    ) -> CreativeContext:
        thinking, scene = require_scene(context)

        shots = await self.policy.plan_shots(scene, thinking)

        thinking.scene = replace(
            scene,
            shots=shots,
            status="planned",
        )
        thinking.record("shot_count", len(shots))

        context.record(
            "planned_scene",
            thinking.scene,
        )

        return context
