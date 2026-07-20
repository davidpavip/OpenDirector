from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from opendirector.planning import SourceDocument


@dataclass(frozen=True)
class ProductionPaths:
    """Canonical paths inside one OpenDirector production workspace."""

    root: Path
    source: Path
    planning: Path
    blueprint: Path
    history: Path

    @classmethod
    def from_root(cls, root: Path) -> "ProductionPaths":
        resolved = root.expanduser().resolve()

        return cls(
            root=resolved,
            source=resolved / "source.md",
            planning=resolved / "planning.md",
            blueprint=resolved / "blueprint.md",
            history=resolved / "history",
        )


class ProductionIO:
    """Read and write human-readable production documents."""

    def load_source(
        self,
        paths: ProductionPaths,
    ) -> SourceDocument:
        if not paths.root.is_dir():
            raise FileNotFoundError(f"Production directory not found: {paths.root}")

        if not paths.source.is_file():
            raise FileNotFoundError(f"Source document not found: {paths.source}")

        content = paths.source.read_text(encoding="utf-8")

        return SourceDocument(
            title=paths.root.name.replace("_", " ").title(),
            content=content,
            metadata={
                "production_path": str(paths.root),
                "input_format": "markdown",
            },
        )

    def save_planning(
        self,
        paths: ProductionPaths,
        markdown: str,
    ) -> Path:
        paths.root.mkdir(
            parents=True,
            exist_ok=True,
        )

        paths.planning.write_text(
            markdown,
            encoding="utf-8",
        )

        return paths.planning

    def save_blueprint(
        self,
        paths: ProductionPaths,
        markdown: str,
        version: int,
    ) -> tuple[Path, Path]:
        paths.root.mkdir(
            parents=True,
            exist_ok=True,
        )
        paths.history.mkdir(
            parents=True,
            exist_ok=True,
        )

        paths.blueprint.write_text(
            markdown,
            encoding="utf-8",
        )

        history_path = paths.history / f"blueprint_v{version}.md"

        history_path.write_text(
            markdown,
            encoding="utf-8",
        )

        return paths.blueprint, history_path
