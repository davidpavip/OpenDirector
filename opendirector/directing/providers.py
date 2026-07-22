from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from opendirector.artifact import Artifact
from opendirector.directing.models import ShotDirection
from opendirector.production import ProductionSpecification
from opendirector.sketching import SketchShot


@dataclass(frozen=True)
class DirectRequest:
    """Input required to prepare one shot direction."""

    production_id: str
    scene_id: str
    scene_title: str

    shot: SketchShot
    keyframe: Artifact
    production_specification: ProductionSpecification


class DirectProvider(ABC):
    """Prepare provider-independent direction for one shot."""

    provider_id: str

    @abstractmethod
    async def direct(
        self,
        request: DirectRequest,
    ) -> ShotDirection:
        raise NotImplementedError


class MockDirectProvider(DirectProvider):
    """Deterministic director used by tests and local development."""

    provider_id = "mock.direct"

    async def direct(
        self,
        request: DirectRequest,
    ) -> ShotDirection:
        shot = request.shot
        specification = request.production_specification

        subject_and_action = shot.purpose

        if shot.continuity:
            subject_and_action = (
                f"{subject_and_action} " f"Maintain continuity: {shot.continuity}"
            )

        notes: list[str] = []

        if shot.creative_notes:
            notes.append(shot.creative_notes)

        if shot.filmmaker_revision:
            notes.append("Filmmaker revision: " f"{shot.filmmaker_revision}")

        lighting_and_style = (
            specification.visual_style
            or "Preserve the established production visual style."
        )

        if specification.tone:
            lighting_and_style = (
                f"{lighting_and_style} " f"The emotional tone is {specification.tone}."
            )

        return ShotDirection(
            production_id=request.production_id,
            scene_id=request.scene_id,
            shot_id=shot.shot_id,
            keyframe_path=str(request.keyframe.location),
            shot_and_camera=shot.camera,
            subject_and_action=subject_and_action,
            performance_and_emotion=(
                "Use natural, restrained performance that supports "
                "the shot purpose and the production tone."
            ),
            lighting_and_style=lighting_and_style,
            narration="",
            acoustic_environment=(
                "Create natural environmental sound appropriate to "
                "the location, action, and emotional tone."
            ),
            motion_guidance=(
                "Preserve the character identity, composition, "
                "lighting, and visual continuity established by the "
                "keyframe. Use coherent subject motion and stable "
                "cinematic camera movement."
            ),
            creative_notes="\n".join(notes),
            metadata={
                "provider_id": self.provider_id,
                "scene_title": request.scene_title,
                "duration_seconds": shot.duration_seconds,
                "orientation": (specification.preferred_orientation),
                "aspect_ratio": specification.aspect_ratio,
                "distribution": specification.distribution,
            },
        )
