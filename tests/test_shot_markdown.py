from pathlib import Path

from opendirector.applications.shot_renderer import (
    ShotMarkdownRenderer,
)
from opendirector.planning import (
    SceneDecision,
    ScenePlanning,
    SceneUnderstanding,
    ShotPlan,
)
from opendirector.production import (
    ProductionStateStore,
    ProductionWorkspace,
)


def build_scene() -> ScenePlanning:
    return ScenePlanning(
        id="scene-001",
        title="The Discovery",
        status="planned",
        understanding=SceneUnderstanding(
            objective=("Introduce the boy and reveal the abandoned robot."),
            emotional_objective=("Create loneliness, curiosity, and hope."),
            story_function="Inciting incident",
            continuity_requirements=(
                "Golden sunset lighting.",
                "The robot remains inactive.",
            ),
            confidence=0.9,
        ),
        decision=SceneDecision(
            selected_idea_ids=(
                "idea-a",
                "idea-c",
            ),
            reasoning=(
                "Combine the quiet discovery with restrained " "firefly movement."
            ),
            confidence=0.91,
        ),
        shots=(
            ShotPlan(
                id="shot-001",
                purpose="Establish the mountain valley.",
                camera="Wide cinematic push-in",
                estimated_duration_seconds=5,
                output_kind="animated_clip",
                notes=("Keep the village visible in the distance.",),
            ),
            ShotPlan(
                id="shot-002",
                purpose="Reveal the metallic hand.",
                camera="Close-up",
                estimated_duration_seconds=4,
                output_kind="animated_clip",
            ),
        ),
    )


def test_renderer_creates_human_editable_document():
    markdown = ShotMarkdownRenderer().render(build_scene())

    assert "artifact: shot-plan" in markdown
    assert "# The Discovery — Shot Plan" in markdown
    assert "### Shot 01 — shot-001" in markdown
    assert "### Shot 02 — shot-002" in markdown
    assert "#### Filmmaker Revision" in markdown
    assert "Wide cinematic push-in" in markdown


def test_shot_plan_contains_no_runtime_provider_data():
    markdown = ShotMarkdownRenderer().render(build_scene())

    assert "provider:" not in markdown.lower()
    assert "model:" not in markdown.lower()
    assert "render_attempt" not in markdown.lower()
    assert "approved_product" not in markdown.lower()


def test_shot_document_round_trip(tmp_path: Path):
    workspace = ProductionWorkspace.from_root(tmp_path / "little_robot")
    scene_workspace = workspace.scene("scene-001")

    store = ProductionStateStore()
    markdown = ShotMarkdownRenderer().render(build_scene())

    saved = store.save_shots(
        scene_workspace,
        markdown,
    )

    loaded = store.load_shots(scene_workspace)

    assert saved.name == "shots.md"
    assert loaded == markdown
