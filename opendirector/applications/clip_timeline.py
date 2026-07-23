from __future__ import annotations

from pathlib import Path
from typing import Any

from opendirector.artifact import Artifact, Kind
from opendirector.clip_timeline import (
    ClipTimeline,
    ClipTimelineMarkdownRenderer,
)
from opendirector.core.timeline_event import TimelineEvent
from opendirector.core.track import Track
from opendirector.directing import (
    ShotDirectionMarkdownParser,
)
from opendirector.production import (
    ProductionStateStore,
    ProductionWorkspace,
)


class ClipTimelineApplication:
    """Create the initial post-production timeline for one clip."""

    def __init__(
        self,
        store: ProductionStateStore | None = None,
        direction_parser: ShotDirectionMarkdownParser | None = None,
        renderer: ClipTimelineMarkdownRenderer | None = None,
    ) -> None:
        self.store = store or ProductionStateStore()
        self.direction_parser = direction_parser or ShotDirectionMarkdownParser()
        self.renderer = renderer or ClipTimelineMarkdownRenderer()

    def run(
        self,
        production_dir: Path,
        scene_id: str,
        shot_id: str,
        clip_path: Path | None = None,
        direction_path: Path | None = None,
        force: bool = False,
    ) -> Path:
        workspace = ProductionWorkspace.from_root(production_dir)
        scene_workspace = workspace.scene(scene_id)

        state = self.store.load_scene(scene_workspace)

        shot_state = state.shots.get(shot_id)

        if shot_state is None:
            raise ValueError(f"Shot not found in runtime state: {shot_id}")

        resolved_clip = self._resolve_clip(
            workspace=workspace,
            shot_state=shot_state,
            clip_path=clip_path,
        )

        resolved_direction = self._resolve_file(
            workspace.root,
            direction_path
            or (scene_workspace.root / "products" / "direction" / f"{shot_id}.md"),
        )

        parsed = self.direction_parser.parse_file(
            resolved_direction,
            production_id=workspace.root.name,
        )

        duration_seconds = self._duration_from_state(shot_state.metadata)

        clip = Artifact(
            production_id=workspace.root.name,
            scene_id=scene_id,
            shot_id=shot_id,
            kind=Kind.VIDEO,
            location=resolved_clip,
            media_type="video/mp4",
            metadata={
                "role": "clip",
                "provider_id": (shot_state.animation_provider),
            },
        )

        timeline = ClipTimeline(
            production_id=workspace.root.name,
            scene_id=scene_id,
            shot_id=shot_id,
            source_clip=clip,
            duration_seconds=duration_seconds,
            metadata={
                "provider_id": (shot_state.animation_provider),
                "animation_mode": (shot_state.animation_mode),
                "has_audio": bool(shot_state.metadata.get("has_audio")),
                "audio_baked_in": bool(shot_state.metadata.get("audio_baked_in")),
            },
        )

        timeline.add_event(
            TimelineEvent.create(
                start=0.0,
                duration=duration_seconds,
                track=Track.VIDEO,
                event_type="video_clip",
                metadata={
                    "description": ("Generated source video."),
                    "artifact_path": str(resolved_clip),
                },
            )
        )

        if shot_state.metadata.get("has_audio"):
            timeline.add_event(
                TimelineEvent.create(
                    start=0.0,
                    duration=duration_seconds,
                    track=Track.NATIVE_AUDIO,
                    event_type="native_audio",
                    metadata={
                        "description": ("Provider-generated native stereo mix."),
                        "artifact_path": str(resolved_clip),
                        "embedded_stream": "audio",
                    },
                )
            )

        direction = parsed.direction

        for dialogue in direction.dialogue:
            timeline.add_event(
                TimelineEvent.create(
                    start=0.0,
                    duration=duration_seconds,
                    track=Track.DIALOGUE,
                    event_type="dialogue",
                    metadata={
                        "text": dialogue.text,
                        "speaker": dialogue.speaker,
                        "delivery": (dialogue.delivery or "Not specified"),
                        "timing": "pending analysis",
                        "source": "shot direction",
                    },
                )
            )

        if direction.narration:
            timeline.add_event(
                TimelineEvent.create(
                    start=0.0,
                    duration=duration_seconds,
                    track=Track.NARRATION,
                    event_type="narration",
                    metadata={
                        "text": direction.narration,
                        "timing": "pending",
                    },
                )
            )

        if direction.acoustic_environment:
            timeline.add_event(
                TimelineEvent.create(
                    start=0.0,
                    duration=duration_seconds,
                    track=Track.AMBIENCE,
                    event_type="ambience_direction",
                    metadata={
                        "description": (direction.acoustic_environment),
                        "source": (
                            "native provider mix or " "future ambience artifact"
                        ),
                    },
                )
            )

        output_directory = scene_workspace.root / "products" / "timeline" / shot_id
        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path = output_directory / "clip.timeline.md"

        if output_path.exists() and not force:
            return output_path

        markdown = self.renderer.render(
            timeline,
            production_root=workspace.root,
        )

        output_path.write_text(
            markdown,
            encoding="utf-8",
        )

        return output_path

    def _resolve_clip(
        self,
        workspace: ProductionWorkspace,
        shot_state: Any,
        clip_path: Path | None,
    ) -> Path:
        value = clip_path

        if value is None:
            if not shot_state.animation_artifact:
                raise ValueError("Shot has no generated clip artifact")

            value = Path(shot_state.animation_artifact)

        return self._resolve_file(
            workspace.root,
            value,
        )

    @staticmethod
    def _duration_from_state(
        metadata: dict[str, Any],
    ) -> float:
        value = metadata.get(
            "duration_seconds",
            5.0,
        )

        if not isinstance(value, int | float):
            raise ValueError("Clip duration is not numeric")

        duration = float(value)

        if duration <= 0:
            raise ValueError("Clip duration must be greater than zero")

        return duration

    @staticmethod
    def _resolve_file(
        root: Path,
        value: Path,
    ) -> Path:
        resolved = (value if value.is_absolute() else root / value).resolve()

        if not resolved.is_file():
            raise FileNotFoundError(f"Required file not found: {resolved}")

        return resolved
