from __future__ import annotations

from abc import ABC, abstractmethod

from opendirector.planning import (
    IdeaCritique,
    SceneDecision,
    SceneIdea,
    ScenePlanning,
    ShotPlan,
)


class ImaginePolicy(ABC):
    @abstractmethod
    async def imagine(
        self,
        scene: ScenePlanning,
    ) -> tuple[SceneIdea, ...]:
        raise NotImplementedError


class CritiquePolicy(ABC):
    @abstractmethod
    async def critique(
        self,
        scene: ScenePlanning,
    ) -> tuple[IdeaCritique, ...]:
        raise NotImplementedError


class DecisionPolicy(ABC):
    @abstractmethod
    async def decide(
        self,
        scene: ScenePlanning,
    ) -> SceneDecision:
        raise NotImplementedError


class ShotPlanningPolicy(ABC):
    @abstractmethod
    async def plan_shots(
        self,
        scene: ScenePlanning,
    ) -> tuple[ShotPlan, ...]:
        raise NotImplementedError


##add deterministic policies
class DeterministicImaginePolicy(ImaginePolicy):
    """Create three distinct scene treatments from its purpose."""

    async def imagine(
        self,
        scene: ScenePlanning,
    ) -> tuple[SceneIdea, ...]:
        understanding = scene.understanding

        return (
            SceneIdea(
                id="idea-a",
                title="Quiet Character Approach",
                description=(
                    f"Present the scene through restrained character "
                    f"behavior. Focus on: {understanding.objective}"
                ),
            ),
            SceneIdea(
                id="idea-b",
                title="Visual Discovery Approach",
                description=(
                    "Reveal the scene's important information through "
                    "composition, environmental detail, and movement."
                ),
            ),
            SceneIdea(
                id="idea-c",
                title="Active Story Beat",
                description=(
                    "Use a clear action or event to express the scene's "
                    "story function and move the relationship forward."
                ),
            ),
        )


class DeterministicCritiquePolicy(CritiquePolicy):
    async def critique(
        self,
        scene: ScenePlanning,
    ) -> tuple[IdeaCritique, ...]:
        if not scene.ideas:
            raise ValueError("Critique requires at least one scene idea")

        critiques: list[IdeaCritique] = []

        for idea in scene.ideas:
            if idea.id == "idea-a":
                critiques.append(
                    IdeaCritique(
                        idea_id=idea.id,
                        strengths=(
                            "Supports emotional clarity.",
                            "Keeps production scope controlled.",
                        ),
                        weaknesses=("May feel slow without strong visual staging.",),
                        risks=("Important story information may be too subtle.",),
                    )
                )
            elif idea.id == "idea-b":
                critiques.append(
                    IdeaCritique(
                        idea_id=idea.id,
                        strengths=(
                            "Creates memorable visual storytelling.",
                            "Can work without dialogue.",
                        ),
                        weaknesses=("May emphasize atmosphere over character.",),
                        risks=("Visual complexity may increase rendering cost.",),
                    )
                )
            else:
                critiques.append(
                    IdeaCritique(
                        idea_id=idea.id,
                        strengths=(
                            "Moves the story forward clearly.",
                            "Creates a strong scene beat.",
                        ),
                        weaknesses=("May reduce the scene's emotional subtlety.",),
                        risks=("Action may overpower the intended tone.",),
                    )
                )

        return tuple(critiques)


class DeterministicDecisionPolicy(DecisionPolicy):
    async def decide(
        self,
        scene: ScenePlanning,
    ) -> SceneDecision:
        if not scene.ideas:
            raise ValueError("Decision requires scene ideas")

        if len(scene.critiques) != len(scene.ideas):
            raise ValueError("Decision requires a critique for every idea")

        selected = scene.ideas[0]

        return SceneDecision(
            selected_idea_ids=(selected.id,),
            reasoning=(
                f"{selected.title} best protects the scene objective "
                "while keeping the scope controlled. The filmmaker may "
                "combine elements from other ideas during revision."
            ),
            confidence=0.80,
        )


class DeterministicShotPlanningPolicy(ShotPlanningPolicy):
    """Translate a scene decision into short rendering units."""

    async def plan_shots(
        self,
        scene: ScenePlanning,
    ) -> tuple[ShotPlan, ...]:
        if scene.decision is None:
            raise ValueError("Shot planning requires a scene decision")

        return (
            ShotPlan(
                id=f"{scene.id}-shot-001",
                purpose=(
                    "Establish the scene location, atmosphere, and "
                    "character positions."
                ),
                camera="Wide establishing shot",
                estimated_duration_seconds=5,
                output_kind="animated_clip",
            ),
            ShotPlan(
                id=f"{scene.id}-shot-002",
                purpose=("Show the primary character action and emotional beat."),
                camera="Medium character shot",
                estimated_duration_seconds=5,
                output_kind="animated_clip",
            ),
            ShotPlan(
                id=f"{scene.id}-shot-003",
                purpose=("Emphasize the most important visual or emotional detail."),
                camera="Close-up",
                estimated_duration_seconds=4,
                output_kind="animated_clip",
            ),
            ShotPlan(
                id=f"{scene.id}-shot-004",
                purpose=(
                    "Resolve the scene beat and prepare continuity "
                    "for the next scene."
                ),
                camera="Wide or tracking exit shot",
                estimated_duration_seconds=6,
                output_kind="animated_clip",
            ),
        )
