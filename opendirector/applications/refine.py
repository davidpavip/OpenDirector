from __future__ import annotations

from pathlib import Path

from opendirector.artifact import Artifact, Kind
from opendirector.production import (
    ProductionSpecificationParser,
    ProductionWorkspace,
)
from opendirector.refining import (
    MockRefineProvider,
    RefineProvider,
    RefineRequest,
)


class RefineApplication:
    """Create keyframes from selected image artifacts."""

    def __init__(
        self,
        provider: RefineProvider | None = None,
        specification_parser: ProductionSpecificationParser | None = None,
    ) -> None:
        self.provider = provider or MockRefineProvider()
        self.specification_parser = (
            specification_parser or ProductionSpecificationParser()
        )

    async def run(
        self,
        production_dir: Path,
        scene_id: str,
        input_path: Path,
        creative_direction: str = "",
    ) -> Artifact:
        workspace = ProductionWorkspace.from_root(production_dir)

        source_path = (
            input_path if input_path.is_absolute() else workspace.root / input_path
        ).resolve()

        if not source_path.is_file():
            raise FileNotFoundError(f"Input image not found: {source_path}")

        source_text = (workspace.root / "source.md").read_text(encoding="utf-8")

        specification = self.specification_parser.parse(source_text)

        shot_id = source_path.stem.split("-keyframe-")[0]

        source_artifact = Artifact(
            production_id=workspace.root.name,
            scene_id=scene_id,
            shot_id=shot_id,
            kind=Kind.IMAGE,
            location=source_path,
            media_type=self._media_type(source_path),
            metadata={
                "role": "refine_source",
            },
        )

        output_directory = workspace.scene(scene_id).root / "products" / "keyframe"

        request = RefineRequest(
            source_artifact=source_artifact,
            production_specification=specification,
            output_directory=output_directory,
            creative_direction=creative_direction,
        )

        return await self.provider.refine(request)

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
