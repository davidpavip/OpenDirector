from __future__ import annotations

from opendirector.planning import (
    IdeaCritique,
    PlanningDocument,
    ProductionBlueprint,
    ProductionUnderstanding,
    SceneDecision,
    SceneIdea,
    ScenePlanning,
    SceneUnderstanding,
    ShotPlan,
)


def build_little_robot_planning(
    blueprint: ProductionBlueprint,
) -> PlanningDocument:
    """Build the first scene-centered planning notebook.

    This is deterministic application content for Production 001.
    Later, the Planner thinking circle will produce these objects.
    """

    return PlanningDocument(
        production_id="little_robot",
        title="The Little Robot",
        status="draft",
        understanding=ProductionUnderstanding(
            intent=blueprint.intent_summary,
            audience=("Family",),
            target_runtime="8–10 minutes",
            themes=(
                "Friendship",
                "Hope",
                "Curiosity",
                "Courage",
            ),
            values=(
                "Human imagination comes first.",
                "Emotion is more important than spectacle.",
                "Simplicity is preferred over complexity.",
                "Every scene must advance the relationship.",
            ),
            constraints=blueprint.constraints,
            unknowns=(
                "Final dialogue level",
                "Final music style",
                "Whether the village is reached in this film",
            ),
            confidence=0.88,
        ),
        scenes=(
            _discovery_scene(),
            _activation_scene(),
            _journey_scene(),
        ),
    )


def _discovery_scene() -> ScenePlanning:
    return ScenePlanning(
        id="scene-001",
        title="The Discovery",
        status="decided",
        understanding=SceneUnderstanding(
            objective=(
                "Introduce the lonely boy and establish curiosity "
                "about the abandoned robot."
            ),
            emotional_objective=(
                "The audience should feel loneliness, curiosity, "
                "wonder, and the beginning of hope."
            ),
            story_function="Inciting incident",
            required_information=(
                "The boy is alone in the mountain valley.",
                "The robot appears abandoned and inactive.",
                "The glowing village is visible in the distance.",
            ),
            continuity_requirements=(
                "Introduce the boy's established appearance.",
                "Introduce the robot before activation.",
                "Establish sunset lighting.",
            ),
            constraints=(
                "No dialogue.",
                "Slow and emotionally quiet pacing.",
                "Do not explain the robot's history.",
            ),
            assumptions=("The robot is mechanical rather than supernatural.",),
            unknowns=("How visibly damaged should the robot appear?",),
            risks=(
                "The reveal may be too subtle.",
                "The opening may feel slow without strong composition.",
            ),
            confidence=0.89,
        ),
        ideas=(
            SceneIdea(
                id="idea-a",
                title="Robot Under the Tree",
                description=(
                    "The boy rests beneath an old tree and notices "
                    "a metallic hand extending from the grass."
                ),
            ),
            SceneIdea(
                id="idea-b",
                title="Robot Beside the Path",
                description=(
                    "The boy hears a faint mechanical sound while "
                    "walking downhill toward the village."
                ),
            ),
            SceneIdea(
                id="idea-c",
                title="Firefly Reveal",
                description=(
                    "Fireflies gather around a hidden metallic form "
                    "and guide the boy toward it."
                ),
            ),
        ),
        critiques=(
            IdeaCritique(
                idea_id="idea-a",
                strengths=(
                    "Quiet and emotionally focused.",
                    "Simple to stage.",
                    "Supports a controlled visual reveal.",
                ),
                weaknesses=("The reveal could be too subtle.",),
                risks=("The robot may blend into the environment.",),
            ),
            IdeaCritique(
                idea_id="idea-b",
                strengths=(
                    "Creates immediate curiosity.",
                    "Suggests that the robot may still function.",
                ),
                weaknesses=("Sound becomes more important than the image.",),
            ),
            IdeaCritique(
                idea_id="idea-c",
                strengths=(
                    "Visually memorable.",
                    "Connects the discovery to the environment.",
                ),
                weaknesses=("May make the robot seem magical.",),
            ),
        ),
        decision=SceneDecision(
            selected_idea_ids=("idea-a", "idea-c"),
            reasoning=(
                "Use the quiet discovery under the tree, while "
                "allowing a few fireflies to strengthen the visual "
                "reveal without making the robot supernatural."
            ),
            confidence=0.91,
        ),
        shots=(
            ShotPlan(
                id="shot-001",
                purpose=(
                    "Establish the valley, distant village, and " "the boy's isolation."
                ),
                camera="Wide, slow cinematic push-in",
                estimated_duration_seconds=5,
                output_kind="animated_clip",
            ),
            ShotPlan(
                id="shot-002",
                purpose=("Introduce the boy resting beneath the tree."),
                camera="Medium observational shot",
                estimated_duration_seconds=5,
                output_kind="animated_clip",
            ),
            ShotPlan(
                id="shot-003",
                purpose=("Reveal the metallic hand beneath the grass."),
                camera="Close-up with shallow movement",
                estimated_duration_seconds=4,
                output_kind="animated_clip",
            ),
            ShotPlan(
                id="shot-004",
                purpose=("Show the boy kneeling beside the inactive robot."),
                camera="Over-the-shoulder",
                estimated_duration_seconds=6,
                output_kind="animated_clip",
            ),
        ),
    )


def _activation_scene() -> ScenePlanning:
    return ScenePlanning(
        id="scene-002",
        title="The First Activation",
        status="ideas",
        understanding=SceneUnderstanding(
            objective=(
                "Show the boy's kindness and establish the robot's "
                "loyal but slightly clumsy personality."
            ),
            emotional_objective=("Move the audience from uncertainty toward trust."),
            story_function="First relationship beat",
            required_information=(
                "The boy attempts a simple repair.",
                "The robot activates unexpectedly.",
                "The robot is awkward rather than threatening.",
            ),
            continuity_requirements=(
                "Continue from the robot's inactive position.",
                "Preserve the same location and twilight progression.",
            ),
            constraints=(
                "Avoid technical exposition.",
                "Keep the repair visually understandable.",
                "The robot must not appear aggressive.",
            ),
            unknowns=(
                "Should the robot speak?",
                "Should the first repair attempt fail?",
            ),
            risks=("The activation could feel too sudden.",),
            confidence=0.81,
        ),
        ideas=(
            SceneIdea(
                id="idea-a",
                title="Silent Activation",
                description=(
                    "The robot's eyes illuminate. It tries to stand "
                    "but gently falls back into the grass."
                ),
            ),
            SceneIdea(
                id="idea-b",
                title="One Broken Word",
                description=(
                    "The robot activates and speaks one incomplete "
                    "word from its forgotten past."
                ),
            ),
            SceneIdea(
                id="idea-c",
                title="Protective Reflex",
                description=(
                    "The robot activates only when the boy slips "
                    "near the edge of the hill."
                ),
            ),
        ),
        filmmaker_notes=("Decide whether the robot should speak before critique."),
    )


def _journey_scene() -> ScenePlanning:
    return ScenePlanning(
        id="scene-003",
        title="The Journey Toward the Village",
        status="understanding",
        understanding=SceneUnderstanding(
            objective=(
                "Move the boy and robot toward the village while "
                "showing their new companionship through action."
            ),
            emotional_objective=(
                "Create warmth, hope, and mild uncertainty about "
                "what waits in the village."
            ),
            story_function="Relationship development",
            required_information=(
                "The robot follows slightly behind the boy.",
                "The village becomes brighter as twilight deepens.",
                "Their companionship is visible without exposition.",
            ),
            continuity_requirements=(
                "Robot remains slightly clumsy.",
                "Golden sunset transitions into blue twilight.",
                "Maintain the established mountain path.",
            ),
            constraints=(
                "Minimal or no dialogue.",
                "Use gentle camera movement.",
            ),
            unknowns=("What obstacle should reveal their growing trust?",),
            risks=("The scene may become visually repetitive.",),
            confidence=0.74,
        ),
    )
