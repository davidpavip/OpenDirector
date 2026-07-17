from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ShotState:
    """Runtime state for one rendering unit."""

    shot_id: str
    status: str = "pending"
    approved_product: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SceneState:
    """Machine-readable current state of one scene."""

    scene_id: str
    title: str = ""
    planning_stage: str = "understanding"
    production_stage: str = "not_started"
    status: str = "draft"

    selected_idea_ids: list[str] = field(default_factory=list)
    continuity: dict[str, Any] = field(default_factory=dict)
    open_questions: list[str] = field(default_factory=list)
    shots: dict[str, ShotState] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "SceneState":
        raw_shots = data.get("shots", {})

        shots = {
            shot_id: ShotState(**shot_data) for shot_id, shot_data in raw_shots.items()
        }

        return cls(
            scene_id=data["scene_id"],
            title=data.get("title", ""),
            planning_stage=data.get(
                "planning_stage",
                "understanding",
            ),
            production_stage=data.get(
                "production_stage",
                "not_started",
            ),
            status=data.get("status", "draft"),
            selected_idea_ids=list(data.get("selected_idea_ids", [])),
            continuity=dict(data.get("continuity", {})),
            open_questions=list(data.get("open_questions", [])),
            shots=shots,
        )


@dataclass
class SceneIndexEntry:
    scene_id: str
    title: str
    order: int
    status: str = "draft"


@dataclass
class ProductionState:
    """Machine-readable current state of the production."""

    production_id: str
    title: str = ""
    status: str = "planning"
    current_scene_id: str | None = None

    global_constraints: list[str] = field(default_factory=list)
    continuity: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "ProductionState":
        return cls(
            production_id=data["production_id"],
            title=data.get("title", ""),
            status=data.get("status", "planning"),
            current_scene_id=data.get("current_scene_id"),
            global_constraints=list(data.get("global_constraints", [])),
            continuity=dict(data.get("continuity", {})),
        )
