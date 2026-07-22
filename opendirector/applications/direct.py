from __future__ import annotations

from pathlib import Path

from opendirector.artifact import Artifact, Kind
from opendirector.directing import (
    DirectProvider,
    DirectRequest,
    MockDirectProvider,
    ShotDirectionMarkdownRenderer,
)
from opendirector.production import (
    ProductionSpecificationParser,
    ProductionStateStore,
    ProductionWorkspace,
)
from opendirector.sketching import ShotMarkdownParser


class DirectApplication:
    """Create direction.md for one planned shot and keyframe."""

    def __init__(
        self,
        provider: DirectProvider | None = None,
        store: ProductionStateStore | None = None,
        shot_parser: ShotMarkdownParser | None = None,
        specification_parser: ProductionSpecificationParser | None = None,
        renderer: ShotDirectionMarkdownRenderer | None = None,
    ) -> None:
        self.provider = provider or MockDirectProvider()
        self.store = store or ProductionStateStore()
        self.shot_parser = shot_parser or ShotMarkdownParser()
        self.specification_parser = (
            specification_parser or ProductionSpecificationParser()
        )
        self.renderer = renderer or ShotDirectionMarkdownRenderer()

    async def run(
        self,
        production_dir: Path,
        scene_id: str,
        shot_id: str,
        keyframe_path: Path,
        force: bool = False,
    ) -> Path:
        workspace = ProductionWorkspace.from_root(production_dir)
        scene_workspace = workspace.scene(scene_id)

        source_path = workspace.root / "source.md"

        if not source_path.is_file():
            raise FileNotFoundError(f"Source document not found: {source_path}")

        resolved_keyframe = (
            keyframe_path
            if keyframe_path.is_absolute()
            else workspace.root / keyframe_path
        ).resolve()

        if not resolved_keyframe.is_file():
            raise FileNotFoundError(f"Keyframe not found: {resolved_keyframe}")

        shots_markdown = self.store.load_shots(scene_workspace)
        shot_document = self.shot_parser.parse(shots_markdown)

        shot = next(
            (
                candidate
                for candidate in shot_document.shots
                if candidate.shot_id == shot_id
            ),
            None,
        )

        if shot is None:
            raise ValueError(f"Shot not found in shots.md: {shot_id}")

        specification = self.specification_parser.parse(
            source_path.read_text(encoding="utf-8")
        )

        keyframe = Artifact(
            production_id=workspace.root.name,
            scene_id=scene_id,
            shot_id=shot_id,
            kind=Kind.IMAGE,
            location=resolved_keyframe,
            media_type=self._media_type(resolved_keyframe),
            metadata={
                "role": "keyframe",
            },
        )

        request = DirectRequest(
            production_id=workspace.root.name,
            scene_id=scene_id,
            scene_title=shot_document.scene_title,
            shot=shot,
            keyframe=keyframe,
            production_specification=specification,
        )

        direction = await self.provider.direct(request)

        output_directory = scene_workspace.root / "products" / "direction"
        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path = output_directory / f"{shot_id}.md"

        if output_path.exists() and not force:
            return output_path

        markdown = self.renderer.render(
            direction,
            production_root=workspace.root,
        )

        output_path.write_text(
            markdown,
            encoding="utf-8",
        )

        return output_path

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
        }.get(
            path.suffix.lower(),
            "application/octet-stream",
        )
