from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import yaml

from .models import Movie, Scene, Shot


class Project:
    """OpenDirector project folder.

    The project is the stable container for story, characters, scenes,
    generated assets, reviews, edit decisions, and exports.
    """

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.project_file = self.root / "project.yaml"
        if not self.project_file.exists():
            raise FileNotFoundError(f"Missing project.yaml: {self.project_file}")
        self.config = self._read_yaml(self.project_file)

    @staticmethod
    def _read_yaml(path: Path) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def path(self, *parts: str) -> Path:
        return self.root.joinpath(*parts)

    def load_movie(self) -> Movie:
        shots_path = self.path("shots", "shots.json")
        if not shots_path.exists():
            return Movie(id=self.config.get("id", "movie"), title=self.config.get("name", "Untitled"))

        shots_data = json.loads(shots_path.read_text(encoding="utf-8"))
        scenes: Dict[str, Scene] = {}

        for item in shots_data:
            scene_id = str(item.get("scene", item.get("scene_id", "scene_001")))
            if scene_id not in scenes:
                scenes[scene_id] = Scene(
                    id=scene_id,
                    title=item.get("scene_title", f"Scene {scene_id}"),
                )
            shot = Shot(
                id=item["shot_id"],
                scene_id=scene_id,
                image_file=item["image_file"],
                video_file=item["video_file"],
                image_prompt=item.get("image_prompt", ""),
                video_prompt=item.get("video_prompt", ""),
                duration=float(item.get("duration", self.config.get("default_duration", 4))),
                camera=item.get("camera"),
                motion=item.get("motion"),
                metadata={k: v for k, v in item.items() if k not in {
                    "shot_id", "scene", "scene_id", "image_file", "video_file",
                    "image_prompt", "video_prompt", "duration", "camera", "motion"
                }},
            )
            scenes[scene_id].shots.append(shot)

        return Movie(
            id=self.config.get("id", "movie"),
            title=self.config.get("name", "Untitled"),
            scenes=list(scenes.values()),
            metadata=self.config,
        )

    def ensure_dirs(self) -> None:
        for rel in [
            "characters", "locations", "scenes", "shots",
            "assets/images", "assets/videos", "review", "edl", "export"
        ]:
            self.path(rel).mkdir(parents=True, exist_ok=True)
