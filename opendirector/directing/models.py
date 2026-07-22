from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DialogueDirection:
    """One spoken line and its intended delivery."""

    speaker: str
    text: str
    delivery: str = ""


@dataclass(frozen=True)
class ShotDirection:
    """Provider-independent creative direction for one shot."""

    production_id: str
    scene_id: str
    shot_id: str

    keyframe_path: str | None = None

    shot_and_camera: str = ""
    subject_and_action: str = ""
    performance_and_emotion: str = ""
    lighting_and_style: str = ""

    dialogue: tuple[DialogueDirection, ...] = ()
    narration: str = ""
    acoustic_environment: str = ""
    motion_guidance: str = ""
    creative_notes: str = ""

    status: str = "draft"
    metadata: dict[str, object] = field(default_factory=dict)
