import asyncio
from pathlib import Path

import pytest
from typer.testing import CliRunner

from opendirector.applications import SketchApplication
from opendirector.artifact import Artifact, Kind
from opendirector.cli.main import app
from opendirector.production import (
    ProductionStateStore,
    ProductionWorkspace,
    SceneState,
    ShotState,
)

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

Establish the mountain valley and the boy's isolation.

#### Camera

Wide cinematic push-in

#### Estimated Duration

5 seconds

#### Intended Output

Animated clip

#### Continuity

Golden sunset. Robot is not visible.

#### Creative Notes

Keep the village visible in the distance.

#### Filmmaker Revision

Use a slightly lower camera angle.

---

### Shot 02 — shot-002

<!-- shot:id=shot-002 -->

#### Purpose

Reveal the robot's metallic hand.

#### Camera

Close-up

#### Estimated Duration

4 seconds

#### Intended Output

Animated clip

#### Continuity

Same sunset lighting.

#### Creative Notes

Keep the reveal subtle.

#### Filmmaker Revision

"""


DEFAULT_SOURCE = """\
Make a 50-second animated movie for X in landscape format.

The story is about a lonely boy and a lost robot.

The tone should be warm and hopeful.

Narration in English.

Generate English and Chinese subtitles.
"""


def prepare_workspace(
    tmp_path: Path,
    source: str = DEFAULT_SOURCE,
) -> tuple[ProductionWorkspace, Path]:
    production_dir = tmp_path / "little_robot"
    production_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    source_path = production_dir / "source.md"
    source_path.write_text(
        source,
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
                "shot-002": ShotState(shot_id="shot-002"),
            },
        ),
    )

    return workspace, production_dir


def run_sketch(
    production_dir: Path,
    force: bool = False,
) -> tuple[Artifact, ...]:
    return asyncio.run(
        SketchApplication().run(
            production_dir=production_dir,
            scene_id="scene-001",
            force=force,
        )
    )


def test_sketch_application_creates_one_artifact_per_shot(
    tmp_path: Path,
):
    workspace, production_dir = prepare_workspace(tmp_path)

    artifacts = run_sketch(production_dir)

    assert len(artifacts) == 2
    assert all(isinstance(artifact, Artifact) for artifact in artifacts)
    assert all(artifact.exists for artifact in artifacts)
    assert all(artifact.kind is Kind.IMAGE for artifact in artifacts)
    assert all(artifact.media_type == "image/svg+xml" for artifact in artifacts)

    scene = workspace.scene("scene-001")

    assert (scene.sketch / "shot-001.svg").is_file()
    assert (scene.sketch / "shot-002.svg").is_file()


def test_sketch_application_updates_runtime_state(
    tmp_path: Path,
):
    workspace, production_dir = prepare_workspace(tmp_path)

    run_sketch(production_dir)

    store = ProductionStateStore()
    state = store.load_scene(workspace.scene("scene-001"))

    assert state.production_stage == "sketched"

    shot = state.shots["shot-001"]

    assert shot.sketch_status == "completed"
    assert shot.sketch_provider == "mock.sketch"
    assert shot.sketch_artifact == ("scenes/scene-001/products/sketch/" "shot-001.svg")

    assert shot.metadata["artifact_id"]
    assert shot.metadata["media_type"] == ("image/svg+xml")


def test_sketch_uses_filmmaker_revision(
    tmp_path: Path,
):
    _, production_dir = prepare_workspace(tmp_path)

    artifacts = run_sketch(production_dir)

    svg = artifacts[0].location.read_text(encoding="utf-8")

    assert "slightly lower camera angle" in svg


def test_sketch_reuses_existing_artifacts_unless_forced(
    tmp_path: Path,
):
    _, production_dir = prepare_workspace(tmp_path)

    first = run_sketch(production_dir)

    original = first[0].location.read_text(encoding="utf-8")

    second = run_sketch(production_dir)

    assert second[0].metadata["reused"] is True
    assert second[0].location == first[0].location
    assert second[0].location.read_text(encoding="utf-8") == original


def test_force_regenerates_existing_artifacts(
    tmp_path: Path,
):
    _, production_dir = prepare_workspace(tmp_path)

    first = run_sketch(production_dir)

    first[0].location.write_text(
        "manually modified",
        encoding="utf-8",
    )

    second = run_sketch(
        production_dir,
        force=True,
    )

    assert second[0].metadata.get("reused") is not True
    assert second[0].location.read_text(encoding="utf-8") != "manually modified"


@pytest.mark.parametrize(
    (
        "source",
        "orientation",
        "aspect_ratio",
        "width",
        "height",
    ),
    [
        (
            """
            Make a 45-second movie for TikTok.

            Use portrait composition.
            """,
            "portrait",
            "9:16",
            540,
            960,
        ),
        (
            """
            Make a 50-second movie for X.

            Use landscape composition.
            """,
            "landscape",
            "16:9",
            960,
            540,
        ),
        (
            """
            Make a short movie for Instagram.

            Use square composition.
            """,
            "square",
            "1:1",
            720,
            720,
        ),
    ],
)
def test_sketch_honors_production_orientation(
    tmp_path: Path,
    source: str,
    orientation: str,
    aspect_ratio: str,
    width: int,
    height: int,
):
    _, production_dir = prepare_workspace(
        tmp_path,
        source=source,
    )

    artifacts = run_sketch(
        production_dir,
        force=True,
    )

    artifact = artifacts[0]

    assert artifact.metadata["orientation"] == (orientation)
    assert artifact.metadata["aspect_ratio"] == (aspect_ratio)
    assert artifact.metadata["canvas_width"] == width
    assert artifact.metadata["canvas_height"] == height

    svg = artifact.location.read_text(encoding="utf-8")

    assert f'width="{width}"' in svg
    assert f'height="{height}"' in svg
    assert f'viewBox="0 0 {width} {height}"' in svg


def test_all_sketches_use_same_production_canvas(
    tmp_path: Path,
):
    source = """\
    Make a 45-second movie for TikTok.

    Use portrait composition.
    """

    _, production_dir = prepare_workspace(
        tmp_path,
        source=source,
    )

    artifacts = run_sketch(
        production_dir,
        force=True,
    )

    assert len(artifacts) == 2

    for artifact in artifacts:
        assert artifact.metadata["orientation"] == ("portrait")
        assert artifact.metadata["aspect_ratio"] == ("9:16")
        assert artifact.metadata["canvas_width"] == 540
        assert artifact.metadata["canvas_height"] == 960


def test_sketch_command_registered():
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["--help"],
    )

    assert result.exit_code == 0
    assert "sketch" in result.stdout
