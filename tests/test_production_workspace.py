from pathlib import Path

from opendirector.production import (
    ProductionState,
    ProductionStateStore,
    ProductionWorkspace,
    SceneIndexEntry,
    SceneState,
    ShotState,
)


def test_workspace_creates_canonical_directories(
    tmp_path: Path,
):
    workspace = ProductionWorkspace.from_root(tmp_path / "little_robot")

    workspace.create()
    scene = workspace.scene("scene-001")
    scene.create()

    assert workspace.scenes.is_dir()
    assert workspace.runtime.is_dir()
    assert workspace.providers.is_dir()
    assert workspace.cache.is_dir()
    assert workspace.logs.is_dir()

    assert scene.artifacts.is_dir()
    assert scene.sketch.is_dir()
    assert scene.animation.is_dir()
    assert scene.audio.is_dir()


def test_production_state_round_trip(tmp_path: Path):
    workspace = ProductionWorkspace.from_root(tmp_path / "little_robot")
    store = ProductionStateStore()

    state = ProductionState(
        production_id="little_robot",
        title="The Little Robot",
        current_scene_id="scene-001",
        global_constraints=["Family-friendly"],
    )

    store.save_production(workspace, state)
    loaded = store.load_production(workspace)

    assert loaded == state


def test_scene_state_round_trip(tmp_path: Path):
    workspace = ProductionWorkspace.from_root(tmp_path / "little_robot")
    scene = workspace.scene("scene-001")
    store = ProductionStateStore()

    state = SceneState(
        scene_id="scene-001",
        title="The Discovery",
        planning_stage="planned",
        selected_idea_ids=["idea-a"],
        shots={
            "shot-001": ShotState(
                shot_id="shot-001",
                status="pending",
            )
        },
    )

    store.save_scene(scene, state)
    loaded = store.load_scene(scene)

    assert loaded == state


def test_scene_index_round_trip(tmp_path: Path):
    workspace = ProductionWorkspace.from_root(tmp_path / "little_robot")
    store = ProductionStateStore()

    entries = [
        SceneIndexEntry(
            scene_id="scene-001",
            title="The Discovery",
            order=1,
            status="planned",
        ),
        SceneIndexEntry(
            scene_id="scene-002",
            title="The First Activation",
            order=2,
            status="ideas",
        ),
    ]

    store.save_scene_index(workspace, entries)
    loaded = store.load_scene_index(workspace)

    assert loaded == entries
