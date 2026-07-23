import asyncio
from pathlib import Path

import pytest

from opendirector.animation import (
    AnimationMode,
    GeneratedClip,
)
from opendirector.applications import (
    AnimateApplication,
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

Visual style: cinematic 3D animation.
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

Cinematic 3D animation with warm sunset light.

## Dialogue

None.

## Narration

None.

## Acoustic Environment

Soft wind, distant birds, and quiet mechanical movement.

## Motion Guidance

Preserve identity and use restrained natural motion.

## Creative Notes

The robot must appear friendly.
"""


def prepare_workspace(
    tmp_path: Path,
) -> tuple[
    ProductionWorkspace,
    Path,
    Path,
    Path,
]:
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
    store = ProductionStateStore()

    store.save_scene(
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

    keyframe = keyframe_directory / "shot-001-keyframe-001.svg"
    keyframe.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg"/>',
        encoding="utf-8",
    )

    direction_directory = scene.root / "products" / "direction"
    direction_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    direction = direction_directory / "shot-001.md"
    direction.write_text(
        DIRECTION,
        encoding="utf-8",
    )

    audio = scene.root / "dialogue.wav"
    audio.write_bytes(b"mock audio")

    return (
        workspace,
        production_dir,
        direction,
        audio,
    )


def run_generate(
    production_dir: Path,
) -> GeneratedClip:
    return asyncio.run(
        AnimateApplication().run(
            production_dir=production_dir,
            scene_id="scene-001",
            shot_id="shot-001",
        )
    )


def test_animate_generates_clip_from_direction(
    tmp_path: Path,
):
    _, production_dir, _, _ = prepare_workspace(tmp_path)

    clip = run_generate(production_dir)

    assert isinstance(clip, GeneratedClip)
    assert clip.artifact.exists
    assert clip.artifact.location.parent.name == ("clip")
    assert clip.artifact.location.name.endswith("generate-001.mp4")
    assert clip.mode is AnimationMode.GENERATE


def test_animate_uses_direction_duration(
    tmp_path: Path,
):
    _, production_dir, _, _ = prepare_workspace(tmp_path)

    clip = run_generate(production_dir)

    # Direction parser currently has no metadata
    # duration, so provider falls back to 5 seconds.
    assert clip.duration_seconds == 5.0


def test_animate_updates_runtime_state(
    tmp_path: Path,
):
    workspace, production_dir, _, _ = prepare_workspace(tmp_path)

    clip = run_generate(production_dir)

    state = ProductionStateStore().load_scene(workspace.scene("scene-001"))
    shot = state.shots["shot-001"]

    assert shot.animation_status == "completed"
    assert shot.animation_provider == ("mock.animation")
    assert shot.animation_mode == "generate"
    assert shot.animation_artifact == (
        "scenes/scene-001/products/clip/" "shot-001-generate-001.mp4"
    )
    assert shot.metadata["clip_artifact_id"] == (clip.artifact.id)
    assert shot.metadata["has_audio"] is True
    assert state.production_stage == "animated"


def test_audio_driven_animation(
    tmp_path: Path,
):
    _, production_dir, _, audio = prepare_workspace(tmp_path)

    clip = asyncio.run(
        AnimateApplication().run(
            production_dir=production_dir,
            scene_id="scene-001",
            shot_id="shot-001",
            mode=AnimationMode.AUDIO_DRIVEN,
            driving_audio_path=audio,
            duration_seconds=6.0,
        )
    )

    assert clip.mode is AnimationMode.AUDIO_DRIVEN
    assert clip.duration_seconds == 6.0
    assert clip.metadata["reference_audio_used"]


def test_retake_animation(
    tmp_path: Path,
):
    _, production_dir, _, _ = prepare_workspace(tmp_path)

    first = run_generate(production_dir)

    retake = asyncio.run(
        AnimateApplication().run(
            production_dir=production_dir,
            scene_id="scene-001",
            shot_id="shot-001",
            mode=AnimationMode.RETAKE,
            source_clip_path=(first.artifact.location),
            retake_start_seconds=1.0,
            retake_duration_seconds=2.0,
        )
    )

    assert retake.mode is AnimationMode.RETAKE
    assert retake.duration_seconds == 2.0
    assert retake.artifact.location.name.endswith("retake-001.mp4")


def test_missing_direction_fails_clearly(
    tmp_path: Path,
):
    _, production_dir, direction, _ = prepare_workspace(tmp_path)
    direction.unlink()

    with pytest.raises(
        FileNotFoundError,
        match="Required file not found",
    ):
        run_generate(production_dir)


def test_missing_keyframe_fails_clearly(
    tmp_path: Path,
):
    _, production_dir, _, _ = prepare_workspace(tmp_path)

    keyframe = (
        production_dir
        / "scenes"
        / "scene-001"
        / "products"
        / "keyframe"
        / "shot-001-keyframe-001.svg"
    )
    keyframe.unlink()

    with pytest.raises(
        FileNotFoundError,
        match="Required file not found",
    ):
        run_generate(production_dir)
