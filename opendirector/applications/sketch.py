from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from opendirector.production import (
    ProductionStateStore,
    ProductionWorkspace,
    SceneState,
    ShotState,
)
from opendirector.sketching import (
    MockSketchProvider,
    SketchProvider,
    SketchRequest,
    ShotMarkdownParser,
)
from opendirector.artifact import Artifact
from opendirector.artifact import Artifact, Kind


class SketchApplication:
    """Create visual sketches from a scene's shots.md contract."""

    def __init__(
        self,
        provider: SketchProvider | None = None,
        parser: ShotMarkdownParser | None = None,
        store: ProductionStateStore | None = None,
    ) -> None:
        self.provider = provider or MockSketchProvider()
        self.parser = parser or ShotMarkdownParser()
        self.store = store or ProductionStateStore()

    async def run(
        self,
        production_dir: Path,
        scene_id: str,
        force: bool = False,
    ) -> tuple[Artifact, ...]:
        workspace = ProductionWorkspace.from_root(production_dir)
        scene_workspace = workspace.scene(scene_id)

        markdown = self.store.load_shots(scene_workspace)
        document = self.parser.parse(markdown)

        if document.scene_id != scene_id:
            raise ValueError(
                f"Requested scene {scene_id!r}, but shots.md "
                f"belongs to {document.scene_id!r}"
            )

        if not document.shots:
            raise ValueError(f"Scene has no planned shots: {scene_id}")

        state = self.store.load_scene(scene_workspace)

        results: list[Artifact] = []

        for shot in document.shots:
            current = state.shots.get(
                shot.shot_id,
                ShotState(shot_id=shot.shot_id),
            )

            if (
                not force
                and current.sketch_status == "completed"
                and current.sketch_artifact
            ):
                existing = (workspace.root / current.sketch_artifact).resolve()

                if existing.is_file():
                    results.append(
                        Artifact(
                            production_id=workspace.root.name,
                            scene_id=scene_id,
                            shot_id=shot.shot_id,
                            kind=Kind.IMAGE,
                            location=existing,
                            media_type=self._media_type(existing),
                            metadata={
                                "provider_id": current.sketch_provider,
                                "reused": True,
                            },
                        )
                    )
                    continue

            request = SketchRequest(
                production_id=workspace.root.name,
                scene_id=scene_id,
                scene_title=document.scene_title,
                shot=shot,
                output_directory=scene_workspace.sketch,
            )

            artifact = await self.provider.sketch(request)
            relative_artifact = artifact.location.relative_to(workspace.root)

            print("relative_artifact =", relative_artifact)
            print("type =", type(relative_artifact))

            state.shots[shot.shot_id] = replace(
                current,
                status="in_progress",
                sketch_status="completed",
                sketch_artifact=str(relative_artifact),
                sketch_provider=artifact.metadata.get("provider_id"),
                metadata={
                    **current.metadata,
                    "camera": shot.camera,
                    "duration_seconds": shot.duration_seconds,
                    "artifact_id": artifact.id,
                    "media_type": artifact.media_type,
                },
            )

            results.append(artifact)

        state = self._complete_scene_sketch_state(state)

        self.store.save_scene(
            scene_workspace,
            state,
        )

        return tuple(results)

    def _complete_scene_sketch_state(
        self,
        state: SceneState,
    ) -> SceneState:
        if state.shots and all(
            shot.sketch_status == "completed" for shot in state.shots.values()
        ):
            state.production_stage = "sketched"

        return state

    def _media_type(self, path: Path) -> str:
        suffix = path.suffix.lower()

        return {
            ".svg": "image/svg+xml",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
        }.get(suffix, "application/octet-stream")
