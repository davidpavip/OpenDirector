import asyncio
from pathlib import Path

from opendirector.applications import RefineApplication
from opendirector.artifact import Artifact, Kind

SOURCE = """\
Make a 50-second movie for X in landscape format.

The story is about a lonely boy and a lost robot.

The tone should be warm and hopeful.
"""


def prepare_source_artifact(
    tmp_path: Path,
) -> tuple[Path, Path]:
    production_dir = tmp_path / "little_robot"
    production_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    (production_dir / "source.md").write_text(
        SOURCE,
        encoding="utf-8",
    )

    sketch_dir = production_dir / "scenes" / "scene-001" / "products" / "sketch"

    sketch_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    sketch_path = sketch_dir / "shot-001.svg"
    sketch_path.write_text(
        """\
<svg xmlns="http://www.w3.org/2000/svg"
     width="960"
     height="540"
     viewBox="0 0 960 540">
</svg>
""",
        encoding="utf-8",
    )

    return production_dir, sketch_path


def run_refine(
    production_dir: Path,
    sketch_path: Path,
    direction: str = "",
) -> Artifact:
    return asyncio.run(
        RefineApplication().run(
            production_dir=production_dir,
            scene_id="scene-001",
            input_path=sketch_path,
            creative_direction=direction,
        )
    )


def test_refine_creates_keyframe_artifact(
    tmp_path: Path,
):
    production_dir, sketch_path = prepare_source_artifact(tmp_path)

    artifact = run_refine(
        production_dir,
        sketch_path,
    )

    assert isinstance(artifact, Artifact)
    assert artifact.kind is Kind.IMAGE
    assert artifact.exists
    assert artifact.location != sketch_path
    assert artifact.media_type == "image/svg+xml"
    assert artifact.metadata["role"] == "keyframe"
    assert artifact.metadata["provider_id"] == ("mock.refine")


def test_refine_preserves_artifact_ownership(
    tmp_path: Path,
):
    production_dir, sketch_path = prepare_source_artifact(tmp_path)

    artifact = run_refine(
        production_dir,
        sketch_path,
    )

    assert artifact.production_id == "little_robot"
    assert artifact.scene_id == "scene-001"
    assert artifact.shot_id == "shot-001"


def test_refine_records_lineage(
    tmp_path: Path,
):
    production_dir, sketch_path = prepare_source_artifact(tmp_path)

    artifact = run_refine(
        production_dir,
        sketch_path,
    )

    assert artifact.metadata["source_artifact_id"]
    assert artifact.metadata["source_location"] == (str(sketch_path))
    assert artifact.metadata["refinement_iteration"] == 1


def test_refine_creates_new_iteration_each_time(
    tmp_path: Path,
):
    production_dir, sketch_path = prepare_source_artifact(tmp_path)

    first = run_refine(
        production_dir,
        sketch_path,
    )

    second = run_refine(
        production_dir,
        first.location,
        direction="Use warmer lighting.",
    )

    assert first.location != second.location
    assert first.location.name.endswith("keyframe-001.svg")
    assert second.location.name.endswith("keyframe-002.svg")
    assert second.metadata["refinement_iteration"] == 2
    assert second.metadata["creative_direction"] == ("Use warmer lighting.")


def test_refine_honors_production_canvas(
    tmp_path: Path,
):
    production_dir, sketch_path = prepare_source_artifact(tmp_path)

    artifact = run_refine(
        production_dir,
        sketch_path,
    )

    assert artifact.metadata["orientation"] == ("landscape")
    assert artifact.metadata["aspect_ratio"] == ("16:9")
    assert artifact.metadata["canvas_width"] == 960
    assert artifact.metadata["canvas_height"] == 540

    svg = artifact.location.read_text(encoding="utf-8")

    assert 'width="960"' in svg
    assert 'height="540"' in svg
    assert 'viewBox="0 0 960 540"' in svg
