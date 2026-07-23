import asyncio
from pathlib import Path

import pytest

from opendirector.animation import (
    AnimationMode,
    AnimationRequest,
    GeneratedClip,
    MockAnimationProvider,
)
from opendirector.artifact import Artifact, Kind
from opendirector.directing import ShotDirection
from opendirector.production import (
    ProductionSpecification,
)


def make_direction() -> ShotDirection:
    return ShotDirection(
        production_id="little_robot",
        scene_id="scene-001",
        shot_id="shot-001",
        keyframe_path=(
            "scenes/scene-001/products/keyframe/" "shot-001-keyframe-001.svg"
        ),
        shot_and_camera=("Medium close-up with a slow push-in."),
        subject_and_action=("The robot opens its eyes and looks " "toward the boy."),
        performance_and_emotion=("The boy moves from caution to hope."),
        acoustic_environment=(
            "Soft wind, distant birds, and a quiet " "mechanical activation sound."
        ),
        metadata={
            "duration_seconds": 5.0,
        },
    )


def make_specification() -> ProductionSpecification:
    return ProductionSpecification(
        creative_profile="movie",
        distribution="x",
        preferred_orientation="landscape",
        target_duration_seconds=50,
        tone="warm and hopeful",
        visual_style="cinematic 3D animation",
    )


def make_image_artifact(
    tmp_path: Path,
) -> Artifact:
    path = tmp_path / "shot-001-keyframe-001.svg"
    path.write_text(
        "<svg></svg>",
        encoding="utf-8",
    )

    return Artifact(
        production_id="little_robot",
        scene_id="scene-001",
        shot_id="shot-001",
        kind=Kind.IMAGE,
        location=path,
        media_type="image/svg+xml",
        metadata={
            "role": "keyframe",
        },
    )


def make_audio_artifact(
    tmp_path: Path,
) -> Artifact:
    path = tmp_path / "dialogue.wav"
    path.write_bytes(b"mock audio")

    return Artifact(
        production_id="little_robot",
        scene_id="scene-001",
        shot_id="shot-001",
        kind=Kind.AUDIO,
        location=path,
        media_type="audio/wav",
        metadata={
            "role": "driving_audio",
        },
    )


def make_video_artifact(
    tmp_path: Path,
) -> Artifact:
    path = tmp_path / "source-clip.mp4"
    path.write_bytes(b"mock video")

    return Artifact(
        production_id="little_robot",
        scene_id="scene-001",
        shot_id="shot-001",
        kind=Kind.VIDEO,
        location=path,
        media_type="video/mp4",
        metadata={
            "role": "clip",
        },
    )


def test_mock_provider_declares_ltx_shaped_capabilities():
    capabilities = MockAnimationProvider.capabilities

    assert capabilities.text_to_video
    assert capabilities.image_to_video
    assert capabilities.audio_to_video
    assert capabilities.retake
    assert capabilities.first_last_frame
    assert capabilities.native_audio


def test_generate_creates_clip_from_keyframe(
    tmp_path: Path,
):
    keyframe = make_image_artifact(tmp_path)

    request = AnimationRequest(
        production_id="little_robot",
        scene_id="scene-001",
        shot_id="shot-001",
        direction=make_direction(),
        production_specification=(make_specification()),
        output_directory=tmp_path / "clips",
        mode=AnimationMode.GENERATE,
        keyframe=keyframe,
    )

    clip = asyncio.run(MockAnimationProvider().animate(request))

    assert isinstance(clip, GeneratedClip)
    assert clip.artifact.kind is Kind.VIDEO
    assert clip.artifact.exists
    assert clip.artifact.media_type == "video/mp4"
    assert clip.mode is AnimationMode.GENERATE
    assert clip.duration_seconds == 5.0
    assert clip.has_audio
    assert clip.audio_baked_in

    assert clip.artifact.metadata["source_keyframe_id"] == keyframe.id
    assert clip.artifact.metadata["animation_mode"] == "generate"


def test_audio_driven_generation_records_audio_lineage(
    tmp_path: Path,
):
    keyframe = make_image_artifact(tmp_path)
    audio = make_audio_artifact(tmp_path)

    request = AnimationRequest(
        production_id="little_robot",
        scene_id="scene-001",
        shot_id="shot-001",
        direction=make_direction(),
        production_specification=(make_specification()),
        output_directory=tmp_path / "clips",
        mode=AnimationMode.AUDIO_DRIVEN,
        keyframe=keyframe,
        driving_audio=audio,
        duration_seconds=6.0,
    )

    clip = asyncio.run(MockAnimationProvider().animate(request))

    assert clip.mode is AnimationMode.AUDIO_DRIVEN
    assert clip.duration_seconds == 6.0
    assert clip.metadata["reference_audio_used"]

    assert clip.artifact.metadata["driving_audio_id"] == audio.id


def test_audio_driven_mode_requires_audio(
    tmp_path: Path,
):
    request = AnimationRequest(
        production_id="little_robot",
        scene_id="scene-001",
        shot_id="shot-001",
        direction=make_direction(),
        production_specification=(make_specification()),
        output_directory=tmp_path / "clips",
        mode=AnimationMode.AUDIO_DRIVEN,
    )

    with pytest.raises(
        ValueError,
        match="requires driving audio",
    ):
        asyncio.run(MockAnimationProvider().animate(request))


def test_retake_records_source_clip_and_time_range(
    tmp_path: Path,
):
    source_clip = make_video_artifact(tmp_path)

    request = AnimationRequest(
        production_id="little_robot",
        scene_id="scene-001",
        shot_id="shot-001",
        direction=make_direction(),
        production_specification=(make_specification()),
        output_directory=tmp_path / "clips",
        mode=AnimationMode.RETAKE,
        source_clip=source_clip,
        retake_start_seconds=1.5,
        retake_duration_seconds=2.5,
    )

    clip = asyncio.run(MockAnimationProvider().animate(request))

    assert clip.mode is AnimationMode.RETAKE
    assert clip.duration_seconds == 2.5

    assert clip.artifact.metadata["source_clip_id"] == source_clip.id
    assert clip.metadata["retake_start_seconds"] == 1.5
    assert clip.metadata["retake_duration_seconds"] == 2.5


def test_retake_requires_source_clip(
    tmp_path: Path,
):
    request = AnimationRequest(
        production_id="little_robot",
        scene_id="scene-001",
        shot_id="shot-001",
        direction=make_direction(),
        production_specification=(make_specification()),
        output_directory=tmp_path / "clips",
        mode=AnimationMode.RETAKE,
        retake_start_seconds=0.0,
        retake_duration_seconds=2.0,
    )

    with pytest.raises(
        ValueError,
        match="requires a source clip",
    ):
        asyncio.run(MockAnimationProvider().animate(request))


def test_each_generation_creates_new_clip_version(
    tmp_path: Path,
):
    keyframe = make_image_artifact(tmp_path)
    provider = MockAnimationProvider()

    request = AnimationRequest(
        production_id="little_robot",
        scene_id="scene-001",
        shot_id="shot-001",
        direction=make_direction(),
        production_specification=(make_specification()),
        output_directory=tmp_path / "clips",
        keyframe=keyframe,
    )

    first = asyncio.run(provider.animate(request))
    second = asyncio.run(provider.animate(request))

    assert first.artifact.location != (second.artifact.location)
    assert first.artifact.location.name.endswith("generate-001.mp4")
    assert second.artifact.location.name.endswith("generate-002.mp4")
