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
    ) -> tuple[Path, ...]:
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

        results: list[Path] = []

        for shot in document.shots:
            current = state.shots.get(
                shot.shot_id,
                ShotState(shot_id=shot.shot_id),
            )

            if (
                not force
                and current.sketch_status == "completed"
                and current.sketch_product
            ):
                existing = (production_dir / current.sketch_product).resolve()

                if existing.is_file():
                    results.append(existing)
                    continue

            request = SketchRequest(
                production_id=workspace.root.name,
                scene_id=scene_id,
                scene_title=document.scene_title,
                shot=shot,
                output_directory=scene_workspace.sketch,
            )

            result = await self.provider.sketch(request)

            relative_product = result.product_path.relative_to(workspace.root)

            state.shots[shot.shot_id] = replace(
                current,
                status="in_progress",
                sketch_status="completed",
                sketch_product=str(relative_product),
                sketch_provider=result.provider_id,
                metadata={
                    **current.metadata,
                    "camera": shot.camera,
                    "duration_seconds": (shot.duration_seconds),
                },
            )

            results.append(result.product_path)

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
