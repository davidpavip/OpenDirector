import asyncio
from pathlib import Path

from opendirector.applications import DirectApplication
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


SHOTS_MARKDOWN = """\
---
artifact: shot-plan
scene: scene-001
title: The Discovery
status: draft
editable_by: filmmaker
---

# The Discovery — Shot Plan

## Shots

### Shot 01 — shot-001

<!-- shot:id=shot-001 -->

#### Purpose

The boy kneels beside the inactive robot as its eyes illuminate.

#### Camera

Medium close-up with a slow cinematic push-in.

#### Estimated Duration

5 seconds

#### Intended Output

Animated clip

#### Continuity

Golden sunset. Keep the village visible in the background.

#### Creative Notes

The robot must appear friendly, not threatening.

#### Filmmaker Revision

Use subtle facial reactions and restrained motion.
"""


def prepare_workspace(
    tmp_path: Path,
) -> tuple[ProductionWorkspace, Path, Path]:
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

    store.save_shots(
        scene,
        SHOTS_MARKDOWN,
    )

    store.save_scene(
        scene,
        SceneState(
            scene_id="scene-001",
            title="The Discovery",
            planning_stage="planned",
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

    keyframe_path = keyframe_directory / "shot-001-keyframe-001.svg"
    keyframe_path.write_text(
        """\
<svg xmlns="http://www.w3.org/2000/svg"
     width="960"
     height="540"
     viewBox="0 0 960 540">
</svg>
""",
        encoding="utf-8",
    )

    return workspace, production_dir, keyframe_path


def run_direct(
    production_dir: Path,
    keyframe_path: Path,
    force: bool = False,
) -> Path:
    return asyncio.run(
        DirectApplication().run(
            production_dir=production_dir,
            scene_id="scene-001",
            shot_id="shot-001",
            keyframe_path=keyframe_path,
            force=force,
        )
    )


def test_direct_creates_direction_markdown(
    tmp_path: Path,
):
    _, production_dir, keyframe_path = prepare_workspace(tmp_path)

    output = run_direct(
        production_dir,
        keyframe_path,
    )

    assert output.is_file()
    assert output.name == "shot-001.md"
    assert output.parent.name == "direction"


def test_direction_contains_core_sections(
    tmp_path: Path,
):
    _, production_dir, keyframe_path = prepare_workspace(tmp_path)

    output = run_direct(
        production_dir,
        keyframe_path,
    )

    markdown = output.read_text(encoding="utf-8")

    assert "## Shot & Camera" in markdown
    assert "## Subject & Action" in markdown
    assert "## Performance & Emotion" in markdown
    assert "## Lighting & Style" in markdown
    assert "## Dialogue" in markdown
    assert "## Narration" in markdown
    assert "## Acoustic Environment" in markdown
    assert "## Motion Guidance" in markdown
    assert "## Creative Notes" in markdown


def test_direction_uses_shot_plan_and_specification(
    tmp_path: Path,
):
    _, production_dir, keyframe_path = prepare_workspace(tmp_path)

    output = run_direct(
        production_dir,
        keyframe_path,
    )

    markdown = output.read_text(encoding="utf-8")

    assert "slow cinematic push-in" in markdown
    assert "cinematic 3D animation" in markdown
    assert "warm and hopeful" in markdown
    assert "friendly, not threatening" in markdown
    assert "subtle facial reactions" in markdown


def test_direction_references_keyframe(
    tmp_path: Path,
):
    _, production_dir, keyframe_path = prepare_workspace(tmp_path)

    output = run_direct(
        production_dir,
        keyframe_path,
    )

    markdown = output.read_text(encoding="utf-8")

    expected = "scenes/scene-001/products/keyframe/" "shot-001-keyframe-001.svg"

    assert f"keyframe: {expected}" in markdown


def test_direction_preserves_filmmaker_edits_unless_forced(
    tmp_path: Path,
):
    _, production_dir, keyframe_path = prepare_workspace(tmp_path)

    output = run_direct(
        production_dir,
        keyframe_path,
    )

    output.write_text(
        "Filmmaker manually edited this file.",
        encoding="utf-8",
    )

    reused = run_direct(
        production_dir,
        keyframe_path,
    )

    assert reused.read_text(encoding="utf-8") == "Filmmaker manually edited this file."

    regenerated = run_direct(
        production_dir,
        keyframe_path,
        force=True,
    )

    assert "## Shot & Camera" in regenerated.read_text(encoding="utf-8")
