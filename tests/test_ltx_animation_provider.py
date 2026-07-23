from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from opendirector.animation import (
    AnimationRequest,
    LTXAnimationProvider,
    LTXOptions,
)
from opendirector.artifact import Artifact, Kind
from opendirector.directing import (
    DialogueDirection,
    ShotDirection,
)
from opendirector.production import (
    ProductionSpecification,
)


class FakeResponse:
    ok = True
    status_code = 200
    content = b"\x00\x00\x00\x18ftypmp42" b"mock-video-content"
    text = ""
    headers = {
        "Content-Type": "video/mp4",
        "x-request-id": "test-request-001",
    }


class FakeSession:
    def __init__(self) -> None:
        self.calls = []

    def post(
        self,
        url,
        *,
        headers,
        json,
        timeout,
    ):
        self.calls.append(
            {
                "url": url,
                "headers": headers,
                "json": json,
                "timeout": timeout,
            }
        )

        return FakeResponse()


def make_request(
    tmp_path: Path,
) -> AnimationRequest:
    keyframe_path = tmp_path / "keyframe.png"
    keyframe_path.write_bytes(b"fake-png")

    keyframe = Artifact(
        production_id="little_robot",
        scene_id="scene-001",
        shot_id="shot-001",
        kind=Kind.IMAGE,
        location=keyframe_path,
        media_type="image/png",
        metadata={"role": "keyframe"},
    )

    direction = ShotDirection(
        production_id="little_robot",
        scene_id="scene-001",
        shot_id="shot-001",
        shot_and_camera=("Medium close-up with a slow push-in."),
        subject_and_action=("The robot opens its eyes."),
        performance_and_emotion=("The boy reacts with cautious hope."),
        lighting_and_style=("Warm cinematic sunset lighting."),
        dialogue=(
            DialogueDirection(
                speaker="Boy",
                text="Are you alive?",
                delivery="quiet and hopeful",
            ),
        ),
        acoustic_environment=("Soft wind and a subtle servo sound."),
        motion_guidance=("Natural restrained movement."),
        metadata={"duration_seconds": 5.0},
    )

    specification = ProductionSpecification(
        creative_profile="movie",
        distribution="x",
        preferred_orientation="landscape",
        target_duration_seconds=50,
        visual_style="cinematic 3D animation",
        tone="warm and hopeful",
    )

    return AnimationRequest(
        production_id="little_robot",
        scene_id="scene-001",
        shot_id="shot-001",
        direction=direction,
        production_specification=specification,
        output_directory=tmp_path / "clips",
        keyframe=keyframe,
        duration_seconds=5.0,
    )


def test_ltx_provider_builds_real_api_request(
    tmp_path: Path,
):
    session = FakeSession()

    provider = LTXAnimationProvider(
        options=LTXOptions(
            model="ltx-2-3-fast",
            generate_audio=True,
        ),
        session=session,
        api_key="test-key",
    )

    clip = asyncio.run(provider.animate(make_request(tmp_path)))

    assert clip.artifact.exists
    assert clip.provider_id == "ltx.video"
    assert clip.duration_seconds == 6.0
    assert clip.has_audio
    assert clip.audio_baked_in

    call = session.calls[0]

    assert call["url"].endswith("/v1/image-to-video")
    assert call["json"]["model"] == ("ltx-2-3-fast")
    assert call["json"]["duration"] == 6
    assert call["json"]["resolution"] == ("1920x1080")
    assert call["json"]["image_uri"].startswith("data:image/png;base64,")
    assert '"Are you alive?"' in (call["json"]["prompt"])


def test_ltx_rejects_svg_keyframe(
    tmp_path: Path,
):
    request = make_request(tmp_path)

    svg_path = tmp_path / "keyframe.svg"
    svg_path.write_text(
        "<svg></svg>",
        encoding="utf-8",
    )

    svg = Artifact(
        production_id="little_robot",
        scene_id="scene-001",
        shot_id="shot-001",
        kind=Kind.IMAGE,
        location=svg_path,
        media_type="image/svg+xml",
    )

    request = AnimationRequest(
        production_id=request.production_id,
        scene_id=request.scene_id,
        shot_id=request.shot_id,
        direction=request.direction,
        production_specification=(request.production_specification),
        output_directory=request.output_directory,
        keyframe=svg,
    )

    provider = LTXAnimationProvider(
        session=FakeSession(),
        api_key="test-key",
    )

    with pytest.raises(
        ValueError,
        match="raster keyframe",
    ):
        asyncio.run(provider.animate(request))
