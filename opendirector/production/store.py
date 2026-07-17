from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from opendirector.production.state import (
    ProductionState,
    SceneIndexEntry,
    SceneState,
)
from opendirector.production.workspace import (
    ProductionWorkspace,
    SceneWorkspace,
)


class ProductionStateStore:
    """Read and write OpenDirector runtime state.

    Providers never write these files directly.
    """

    def initialize(
        self,
        workspace: ProductionWorkspace,
        production_state: ProductionState,
    ) -> None:
        workspace.create()

        if not workspace.production_state.exists():
            self.save_production(
                workspace,
                production_state,
            )

        if not workspace.scene_index.exists():
            self.save_scene_index(workspace, [])

    def save_production(
        self,
        workspace: ProductionWorkspace,
        state: ProductionState,
    ) -> Path:
        workspace.create()
        self._write_json(
            workspace.production_state,
            state.to_dict(),
        )
        return workspace.production_state

    def load_production(
        self,
        workspace: ProductionWorkspace,
    ) -> ProductionState:
        data = self._read_json(workspace.production_state)
        return ProductionState.from_dict(data)

    def save_scene(
        self,
        workspace: SceneWorkspace,
        state: SceneState,
    ) -> Path:
        workspace.create()
        self._write_json(
            workspace.state,
            state.to_dict(),
        )
        return workspace.state

    def load_scene(
        self,
        workspace: SceneWorkspace,
    ) -> SceneState:
        data = self._read_json(workspace.state)
        return SceneState.from_dict(data)

    def save_scene_index(
        self,
        workspace: ProductionWorkspace,
        entries: list[SceneIndexEntry],
    ) -> Path:
        workspace.create()

        payload = {
            "scenes": [
                {
                    "scene_id": entry.scene_id,
                    "title": entry.title,
                    "order": entry.order,
                    "status": entry.status,
                }
                for entry in entries
            ]
        }

        self._write_json(
            workspace.scene_index,
            payload,
        )
        return workspace.scene_index

    def load_scene_index(
        self,
        workspace: ProductionWorkspace,
    ) -> list[SceneIndexEntry]:
        data = self._read_json(workspace.scene_index)

        return [SceneIndexEntry(**entry) for entry in data.get("scenes", [])]

    def _write_json(
        self,
        path: Path,
        data: dict[str, Any],
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(
            json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

    def _read_json(
        self,
        path: Path,
    ) -> dict[str, Any]:
        if not path.is_file():
            raise FileNotFoundError(f"State file not found: {path}")

        value = json.loads(path.read_text(encoding="utf-8"))

        if not isinstance(value, dict):
            raise ValueError(f"State file must contain a JSON object: {path}")

        return value

    def save_shots(
        self,
        workspace: SceneWorkspace,
        markdown: str,
    ) -> Path:
        """Save the filmmaker-editable shot-plan document."""

        workspace.create()

        workspace.shots.write_text(
            markdown,
            encoding="utf-8",
        )

        return workspace.shots

    def load_shots(
        self,
        workspace: SceneWorkspace,
    ) -> str:
        """Load the current filmmaker-edited shot plan."""

        if not workspace.shots.is_file():
            raise FileNotFoundError(f"Shot-plan document not found: {workspace.shots}")

        return workspace.shots.read_text(encoding="utf-8")
