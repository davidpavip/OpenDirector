from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from opendirector.animation import (
    AnimationMode,
    AnimationProvider,
    AnimationRequest,
    GeneratedClip,
    MockAnimationProvider,
)
from opendirector.artifact import Artifact, Kind
from opendirector.directing import (
    ShotDirectionMarkdownParser,
)
from opendirector.production import (
    ProductionSpecificationParser,
    ProductionStateStore,
    ProductionWorkspace,
    ShotState,
)


class AnimateApplication:
    """Generate or revise one shot clip."""

    def __init__(
        self,
        provider: AnimationProvider | None = None,
        store: ProductionStateStore | None = None,
        direction_parser: ShotDirectionMarkdownParser | None = None,
        specification_parser: ProductionSpecificationParser | None = None,
    ) -> None:
        self.provider = provider or MockAnimationProvider()
        self.store = store or ProductionStateStore()
        self.direction_parser = direction_parser or ShotDirectionMarkdownParser()
        self.specification_parser = (
            specification_parser or ProductionSpecificationParser()
        )

    async def run(
        self,
        production_dir: Path,
        scene_id: str,
        shot_id: str,
        direction_path: Path | None = None,
        keyframe_path: Path | None = None,
        mode: AnimationMode = (AnimationMode.GENERATE),
        driving_audio_path: Path | None = None,
        source_clip_path: Path | None = None,
        duration_seconds: float | None = None,
        retake_start_seconds: float | None = None,
        retake_duration_seconds: float | None = None,
    ) -> GeneratedClip:
        workspace = ProductionWorkspace.from_root(production_dir)
        scene_workspace = workspace.scene(scene_id)

        source_path = workspace.root / "source.md"

        if not source_path.is_file():
            raise FileNotFoundError(f"Source document not found: " f"{source_path}")

        resolved_direction = self._resolve_path(
            workspace.root,
            direction_path
            or (scene_workspace.root / "products" / "direction" / f"{shot_id}.md"),
        )

        parsed = self.direction_parser.parse_file(
            resolved_direction,
            production_id=workspace.root.name,
        )
        direction = parsed.direction

        if direction.scene_id != scene_id:
            raise ValueError(
                f"Direction belongs to scene "
                f"{direction.scene_id!r}, not "
                f"{scene_id!r}"
            )

        if direction.shot_id != shot_id:
            raise ValueError(
                f"Direction belongs to shot "
                f"{direction.shot_id!r}, not "
                f"{shot_id!r}"
            )

        specification = self.specification_parser.parse(
            source_path.read_text(encoding="utf-8")
        )

        resolved_keyframe = keyframe_path

        if resolved_keyframe is None and parsed.keyframe_path:
            resolved_keyframe = Path(parsed.keyframe_path)

        keyframe = self._optional_artifact(
            root=workspace.root,
            value=resolved_keyframe,
            production_id=workspace.root.name,
            scene_id=scene_id,
            shot_id=shot_id,
            kind=Kind.IMAGE,
            role="keyframe",
        )

        driving_audio = self._optional_artifact(
            root=workspace.root,
            value=driving_audio_path,
            production_id=workspace.root.name,
            scene_id=scene_id,
            shot_id=shot_id,
            kind=Kind.AUDIO,
            role="driving_audio",
        )

        source_clip = self._optional_artifact(
            root=workspace.root,
            value=source_clip_path,
            production_id=workspace.root.name,
            scene_id=scene_id,
            shot_id=shot_id,
            kind=Kind.VIDEO,
            role="source_clip",
        )

        output_directory = scene_workspace.root / "products" / "clip"

        request = AnimationRequest(
            production_id=workspace.root.name,
            scene_id=scene_id,
            shot_id=shot_id,
            direction=direction,
            production_specification=specification,
            output_directory=output_directory,
            mode=mode,
            keyframe=keyframe,
            driving_audio=driving_audio,
            source_clip=source_clip,
            duration_seconds=duration_seconds,
            retake_start_seconds=(retake_start_seconds),
            retake_duration_seconds=(retake_duration_seconds),
        )

        clip = await self.provider.animate(request)

        self._update_state(
            workspace=workspace,
            scene_id=scene_id,
            shot_id=shot_id,
            clip=clip,
        )

        return clip

    def _update_state(
        self,
        workspace: ProductionWorkspace,
        scene_id: str,
        shot_id: str,
        clip: GeneratedClip,
    ) -> None:
        scene_workspace = workspace.scene(scene_id)
        state = self.store.load_scene(scene_workspace)

        current = state.shots.get(
            shot_id,
            ShotState(shot_id=shot_id),
        )

        relative_path = clip.artifact.location.resolve().relative_to(
            workspace.root.resolve()
        )

        state.shots[shot_id] = replace(
            current,
            status="in_progress",
            animation_status="completed",
            animation_artifact=str(relative_path),
            animation_provider=clip.provider_id,
            animation_mode=clip.mode.value,
            metadata={
                **current.metadata,
                "clip_artifact_id": (clip.artifact.id),
                "clip_media_type": (clip.artifact.media_type),
                "duration_seconds": (clip.duration_seconds),
                "has_audio": clip.has_audio,
                "audio_baked_in": (clip.audio_baked_in),
            },
        )

        if state.shots and all(
            shot.animation_status == "completed" for shot in state.shots.values()
        ):
            state.production_stage = "animated"
        else:
            state.production_stage = "animation_in_progress"

        self.store.save_scene(
            scene_workspace,
            state,
        )

    @staticmethod
    def _resolve_path(
        root: Path,
        value: Path,
    ) -> Path:
        resolved = (value if value.is_absolute() else root / value).resolve()

        if not resolved.is_file():
            raise FileNotFoundError(f"Required file not found: {resolved}")

        return resolved

    def _optional_artifact(
        self,
        root: Path,
        value: Path | None,
        production_id: str,
        scene_id: str,
        shot_id: str,
        kind: Kind,
        role: str,
    ) -> Artifact | None:
        if value is None:
            return None

        path = self._resolve_path(
            root,
            value,
        )

        return Artifact(
            production_id=production_id,
            scene_id=scene_id,
            shot_id=shot_id,
            kind=kind,
            location=path,
            media_type=self._media_type(path),
            metadata={
                "role": role,
            },
        )

    @staticmethod
    def _media_type(
        path: Path,
    ) -> str:
        return {
            ".svg": "image/svg+xml",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".wav": "audio/wav",
            ".mp3": "audio/mpeg",
            ".m4a": "audio/mp4",
            ".mp4": "video/mp4",
            ".mov": "video/quicktime",
        }.get(
            path.suffix.lower(),
            "application/octet-stream",
        )
