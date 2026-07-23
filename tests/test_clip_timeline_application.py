import asyncio
from pathlib import Path

from opendirector.applications import (
    AnimateApplication,
    ClipTimelineApplication,
)
from opendirector.production import (
    ProductionStateStore,
    ProductionWorkspace,
    SceneState,
    ShotState,
)

SOURCE = """\
Make a 50-second movie for X in landscape format.

The story is about a lonely boy and a lost robot.

The tone should be warm and hopeful.
"""


DIRECTION = """\
---
artifact: shot-direction
scene: scene-001
shot: shot-001
status: draft
editable_by: filmmaker
keyframe: scenes/scene-001/products/keyframe/shot-001-keyframe-001.svg
---

# shot-001 — Direction

## Shot & Camera

Medium close-up with a slow push-in.

## Subject & Action

The robot opens its eyes and looks toward the boy.

## Performance & Emotion

The boy moves from caution to hope.

## Lighting & Style

Warm cinematic 3D animation.

## Dialogue

### Boy

"Are you alive?"

Delivery: quiet, cautious, hopeful.

## Narration

A lonely boy finally discovers that he may not be alone.

## Acoustic Environment

Soft wind through grass, distant birds, and a subtle robot servo sound.

## Motion Guidance

Use restrained natural movement.

## Creative Notes

Keep the robot friendly.
"""


def prepare_workspace(
    tmp_path: Path,
) -> tuple[ProductionWorkspace, Path]:
    production_dir = tmp_path / "little_robot"
    production_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    (production_dir / "source.md").write_text(
        SOURCE,
        encoding="utf-8",
    )

    workspace = ProductionWorkspace.from_root(production_dir)
    scene = workspace.scene("scene-001")

    ProductionStateStore().save_scene(
        scene,
        SceneState(
            scene_id="scene-001",
            title="The Discovery",
            planning_stage="planned",
            production_stage="keyframed",
            shots={
                "shot-001": ShotState(shot_id="shot-001"),
            },
        ),
    )

    keyframe_directory = scene.root / "products" / "keyframe"
    keyframe_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    (keyframe_directory / "shot-001-keyframe-001.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg"/>',
        encoding="utf-8",
    )

    direction_directory = scene.root / "products" / "direction"
    direction_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    (direction_directory / "shot-001.md").write_text(
        DIRECTION,
        encoding="utf-8",
    )

    asyncio.run(
        AnimateApplication().run(
            production_dir=production_dir,
            scene_id="scene-001",
            shot_id="shot-001",
        )
    )

    return workspace, production_dir


def test_clip_timeline_is_created(
    tmp_path: Path,
):
    _, production_dir = prepare_workspace(tmp_path)

    output = ClipTimelineApplication().run(
        production_dir=production_dir,
        scene_id="scene-001",
        shot_id="shot-001",
    )

    assert output.is_file()
    assert output.name == "clip.timeline.md"
    assert output.parent.name == "shot-001"


def test_clip_timeline_contains_source_media(
    tmp_path: Path,
):
    _, production_dir = prepare_workspace(tmp_path)

    output = ClipTimelineApplication().run(
        production_dir=production_dir,
        scene_id="scene-001",
        shot_id="shot-001",
    )

    markdown = output.read_text(encoding="utf-8")

    assert "## Video" in markdown
    assert "## Native Audio" in markdown
    assert "mock.animation" in markdown
    assert "shot-001-generate-001.mp4" in markdown


def test_clip_timeline_contains_postproduction_plans(
    tmp_path: Path,
):
    _, production_dir = prepare_workspace(tmp_path)

    output = ClipTimelineApplication().run(
        production_dir=production_dir,
        scene_id="scene-001",
        shot_id="shot-001",
    )

    markdown = output.read_text(encoding="utf-8")

    assert "## Dialogue" in markdown
    assert "Are you alive?" in markdown
    assert "quiet, cautious, hopeful" in markdown

    assert "## Narration" in markdown
    assert "may not be alone" in markdown

    assert "## Ambience" in markdown
    assert "Soft wind through grass" in markdown

    assert "## Music" in markdown
    assert "## Sound Effects" in markdown
    assert "## Subtitles" in markdown


def test_timeline_uses_srt_style_timestamps(
    tmp_path: Path,
):
    _, production_dir = prepare_workspace(tmp_path)

    output = ClipTimelineApplication().run(
        production_dir=production_dir,
        scene_id="scene-001",
        shot_id="shot-001",
    )

    markdown = output.read_text(encoding="utf-8")

    assert "00:00:00,000 --> 00:00:05,000" in markdown


def test_existing_timeline_is_preserved_unless_forced(
    tmp_path: Path,
):
    _, production_dir = prepare_workspace(tmp_path)

    application = ClipTimelineApplication()

    output = application.run(
        production_dir=production_dir,
        scene_id="scene-001",
        shot_id="shot-001",
    )

    output.write_text(
        "Filmmaker edited timeline.",
        encoding="utf-8",
    )

    reused = application.run(
        production_dir=production_dir,
        scene_id="scene-001",
        shot_id="shot-001",
    )

    assert reused.read_text(encoding="utf-8") == "Filmmaker edited timeline."

    regenerated = application.run(
        production_dir=production_dir,
        scene_id="scene-001",
        shot_id="shot-001",
        force=True,
    )

    assert "# shot-001 — Clip Timeline" in (regenerated.read_text(encoding="utf-8"))
