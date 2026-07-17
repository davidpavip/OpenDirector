from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProductionWorkspace:
    """Canonical filesystem layout for one production."""

    root: Path
    source: Path
    planning: Path
    blueprint: Path
    scenes: Path
    runtime: Path
    production_state: Path
    scene_index: Path
    providers: Path
    cache: Path
    logs: Path

    @classmethod
    def from_root(
        cls,
        root: Path,
    ) -> "ProductionWorkspace":
        resolved = root.expanduser().resolve()
        runtime = resolved / ".opendirector"

        return cls(
            root=resolved,
            source=resolved / "source.md",
            planning=resolved / "planning.md",
            blueprint=resolved / "blueprint.md",
            scenes=resolved / "scenes",
            runtime=runtime,
            production_state=runtime / "production.json",
            scene_index=runtime / "scene_index.json",
            providers=runtime / "providers",
            cache=runtime / "cache",
            logs=runtime / "logs",
        )

    def scene(self, scene_id: str) -> "SceneWorkspace":
        normalized = scene_id.strip()

        if not normalized:
            raise ValueError("Scene id cannot be empty")

        return SceneWorkspace.from_root(
            root=self.scenes / normalized,
            scene_id=normalized,
        )

    def create(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.scenes.mkdir(parents=True, exist_ok=True)
        self.runtime.mkdir(parents=True, exist_ok=True)
        self.providers.mkdir(parents=True, exist_ok=True)
        self.cache.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class SceneWorkspace:
    """Canonical filesystem layout for one scene."""

    scene_id: str
    root: Path
    artifacts: Path
    products: Path
    sketch: Path
    animation: Path
    audio: Path
    state: Path
    shots: Path

    @classmethod
    def from_root(
        cls,
        root: Path,
        scene_id: str,
    ) -> "SceneWorkspace":
        normalized = scene_id.strip()

        if not normalized:
            raise ValueError("Scene id cannot be empty")

        resolved = root.expanduser().resolve()
        products = resolved / "products"

        return cls(
            scene_id=normalized,
            root=resolved,
            artifacts=resolved / "artifacts",
            products=products,
            sketch=products / "sketch",
            animation=products / "animation",
            audio=products / "audio",
            state=resolved / "state.json",
            shots=resolved / "shots.md",
        )

    def create(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.artifacts.mkdir(parents=True, exist_ok=True)
        self.products.mkdir(parents=True, exist_ok=True)
        self.sketch.mkdir(parents=True, exist_ok=True)
        self.animation.mkdir(parents=True, exist_ok=True)
        self.audio.mkdir(parents=True, exist_ok=True)
