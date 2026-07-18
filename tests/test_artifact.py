from pathlib import Path

import pytest

from opendirector.artifact import Artifact, Kind


def test_production_owned_artifact():
    artifact = Artifact(
        production_id="little_robot",
        kind=Kind.DOCUMENT,
        location=Path("planning.md"),
        media_type="text/markdown",
    )

    assert artifact.scope == "production"
    assert artifact.scene_id is None
    assert artifact.shot_id is None
    assert artifact.filename == "planning.md"


def test_scene_owned_artifact():
    artifact = Artifact(
        production_id="little_robot",
        scene_id="scene-001",
        kind=Kind.DOCUMENT,
        location=Path("scenes/scene-001/shots.md"),
        media_type="text/markdown",
    )

    assert artifact.scope == "scene"


def test_shot_owned_artifact():
    artifact = Artifact(
        production_id="little_robot",
        scene_id="scene-001",
        shot_id="shot-001",
        kind=Kind.IMAGE,
        location=Path("scenes/scene-001/artifacts/" "sketch/shot-001.svg"),
        media_type="image/svg+xml",
    )

    assert artifact.scope == "shot"
    assert artifact.kind is Kind.IMAGE


def test_shot_artifact_requires_scene():
    with pytest.raises(
        ValueError,
        match="must also belong to a scene",
    ):
        Artifact(
            production_id="little_robot",
            shot_id="shot-001",
            kind=Kind.VIDEO,
            location=Path("shot-001.mp4"),
            media_type="video/mp4",
        )


@pytest.mark.parametrize(
    ("field_name", "kwargs", "message"),
    [
        (
            "production_id",
            {"production_id": " "},
            "production_id cannot be empty",
        ),
        (
            "scene_id",
            {
                "production_id": "little_robot",
                "scene_id": " ",
            },
            "scene_id cannot be empty",
        ),
        (
            "shot_id",
            {
                "production_id": "little_robot",
                "scene_id": "scene-001",
                "shot_id": " ",
            },
            "shot_id cannot be empty",
        ),
    ],
)
def test_artifact_rejects_empty_identifiers(
    field_name: str,
    kwargs: dict[str, str],
    message: str,
):
    del field_name

    with pytest.raises(ValueError, match=message):
        Artifact(
            kind=Kind.DOCUMENT,
            location=Path("artifact.md"),
            media_type="text/markdown",
            **kwargs,
        )


def test_artifact_reports_existing_location(
    tmp_path: Path,
):
    location = tmp_path / "source.md"
    location.write_text(
        "# Source\n",
        encoding="utf-8",
    )

    artifact = Artifact(
        production_id="little_robot",
        kind=Kind.DOCUMENT,
        location=location,
        media_type="text/markdown",
    )

    assert artifact.exists is True


def test_artifact_accepts_arbitrary_metadata():
    artifact = Artifact(
        production_id="little_robot",
        scene_id="scene-001",
        shot_id="shot-001",
        kind=Kind.VIDEO,
        location=Path("shot-001.mp4"),
        media_type="video/mp4",
        metadata={
            "duration_seconds": 6,
            "fps": 24,
        },
    )

    assert artifact.metadata["duration_seconds"] == 6
    assert artifact.metadata["fps"] == 24
