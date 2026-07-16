from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SceneIdea:
    """One possible creative direction for a scene."""

    id: str
    title: str
    description: str

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("SceneIdea id cannot be empty")

        if not self.title.strip():
            raise ValueError("SceneIdea title cannot be empty")

        if not self.description.strip():
            raise ValueError("SceneIdea description cannot be empty")


@dataclass(frozen=True)
class IdeaCritique:
    """Evaluation of one scene idea."""

    idea_id: str
    strengths: tuple[str, ...] = ()
    weaknesses: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.idea_id.strip():
            raise ValueError("IdeaCritique idea_id cannot be empty")


@dataclass(frozen=True)
class SceneDecision:
    """Selected creative direction for a scene."""

    selected_idea_ids: tuple[str, ...]
    reasoning: str
    confidence: float = 0.5

    def __post_init__(self) -> None:
        if not self.selected_idea_ids:
            raise ValueError("SceneDecision requires at least one selected idea")

        if not self.reasoning.strip():
            raise ValueError("SceneDecision reasoning cannot be empty")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("SceneDecision confidence must be between 0 and 1")


@dataclass(frozen=True)
class ShotPlan:
    """One visual rendering unit inside a scene."""

    id: str
    purpose: str
    camera: str
    estimated_duration_seconds: float
    output_kind: str = "animated_clip"
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("ShotPlan id cannot be empty")

        if not self.purpose.strip():
            raise ValueError("ShotPlan purpose cannot be empty")

        if self.estimated_duration_seconds <= 0:
            raise ValueError("ShotPlan duration must be greater than zero")


@dataclass(frozen=True)
class SceneUnderstanding:
    """What the Planner understands about one proposed scene."""

    objective: str
    emotional_objective: str
    story_function: str

    required_information: tuple[str, ...] = ()
    continuity_requirements: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    unknowns: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()
    confidence: float = 0.5

    def __post_init__(self) -> None:
        if not self.objective.strip():
            raise ValueError("SceneUnderstanding objective cannot be empty")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("SceneUnderstanding confidence must be between 0 and 1")


@dataclass(frozen=True)
class ScenePlanning:
    """Complete visible thinking cycle for one proposed scene."""

    id: str
    title: str
    understanding: SceneUnderstanding

    ideas: tuple[SceneIdea, ...] = ()
    critiques: tuple[IdeaCritique, ...] = ()
    decision: SceneDecision | None = None
    shots: tuple[ShotPlan, ...] = ()

    filmmaker_notes: str = ""
    status: str = "draft"

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("ScenePlanning id cannot be empty")

        if not self.title.strip():
            raise ValueError("ScenePlanning title cannot be empty")


@dataclass(frozen=True)
class ProductionUnderstanding:
    """Production-level understanding shared by all scenes."""

    intent: str
    audience: tuple[str, ...] = ()
    target_runtime: str = ""
    values: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    themes: tuple[str, ...] = ()
    unknowns: tuple[str, ...] = ()
    confidence: float = 0.5

    def __post_init__(self) -> None:
        if not self.intent.strip():
            raise ValueError("ProductionUnderstanding intent cannot be empty")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "ProductionUnderstanding confidence must be " "between 0 and 1"
            )


@dataclass(frozen=True)
class PlanningDocument:
    """Human-editable scene-centered planning notebook."""

    production_id: str
    title: str
    understanding: ProductionUnderstanding
    scenes: tuple[ScenePlanning, ...] = ()

    status: str = "draft"
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.production_id.strip():
            raise ValueError("PlanningDocument production_id cannot be empty")

        if not self.title.strip():
            raise ValueError("PlanningDocument title cannot be empty")
