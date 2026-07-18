import asyncio
from pathlib import Path

from opendirector.applications import SketchApplication
from opendirector.production import (
    ProductionStateStore,
    ProductionWorkspace,
    SceneState,
    ShotState,
)

from opendirector.artifact import Artifact, Kind

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


def prepare_workspace(
    tmp_path: Path,
) -> tuple[ProductionWorkspace, Path]:
    production_dir = tmp_path / "little_robot"
    workspace = ProductionWorkspace.from_root(production_dir)
    scene = workspace.scene("scene-001")
    store = ProductionStateStore()

    store.save_shots(scene, SHOTS_MARKDOWN)

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


def test_sketch_application_creates_one_product_per_shot(
    tmp_path: Path,
):
    workspace, production_dir = prepare_workspace(tmp_path)

    artifacts = asyncio.run(
        SketchApplication().run(
            production_dir=production_dir,
            scene_id="scene-001",
        )
    )

    assert len(artifacts) == 2
    assert all(artifact.exists for artifact in artifacts)
    assert all(artifact.kind is Kind.IMAGE for artifact in artifacts)
    assert artifacts[0].location.suffix == ".svg"

    scene = workspace.scene("scene-001")
    assert (scene.sketch / "shot-001.svg").is_file()
    assert (scene.sketch / "shot-002.svg").is_file()


def test_sketch_application_updates_runtime_state(
    tmp_path: Path,
):
    workspace, production_dir = prepare_workspace(tmp_path)

    asyncio.run(
        SketchApplication().run(
            production_dir=production_dir,
            scene_id="scene-001",
        )
    )

    store = ProductionStateStore()
    state = store.load_scene(workspace.scene("scene-001"))

    assert state.production_stage == "sketched"

    shot = state.shots["shot-001"]

    assert shot.sketch_status == "completed"
    assert shot.sketch_provider == "mock.sketch"
    assert shot.sketch_artifact == ("scenes/scene-001/products/sketch/" "shot-001.svg")


def test_sketch_uses_filmmaker_revision(
    tmp_path: Path,
):
    _, production_dir = prepare_workspace(tmp_path)

    artifacts = asyncio.run(
        SketchApplication().run(
            production_dir=production_dir,
            scene_id="scene-001",
        )
    )

    svg = artifacts[0].location.read_text(encoding="utf-8")

    assert "slightly lower camera angle" in svg

def test_sketch_skips_existing_artifacts_unless_forced(
    tmp_path: Path,
):
    _, production_dir = prepare_workspace(tmp_path)
    application = SketchApplication()

    first = asyncio.run(
        application.run(
            production_dir=production_dir,
            scene_id="scene-001",
        )
    )

    original = first[0].location.read_text(encoding="utf-8")

    second = asyncio.run(
        application.run(
            production_dir=production_dir,
            scene_id="scene-001",
        )
    )

    assert second[0].metadata["reused"] is True
    assert second[0].location.read_text(encoding="utf-8") == original


def test_sketch_application_returns_artifacts(
    tmp_path: Path,
):
    _, production_dir = prepare_workspace(tmp_path)

    artifacts = asyncio.run(
        SketchApplication().run(
            production_dir=production_dir,
            scene_id="scene-001",
        )
    )

    assert all(isinstance(artifact, Artifact) for artifact in artifacts)


from typer.testing import CliRunner

from opendirector.cli.main import app

runner = CliRunner()


def test_sketch_command_registered():
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "sketch" in result.stdout
