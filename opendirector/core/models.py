from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class Asset:
    id: str
    path: str
    type: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Character:
    id: str
    name: str
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Location:
    id: str
    name: str
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Shot:
    id: str
    scene_id: str
    image_file: str
    video_file: str
    image_prompt: str
    video_prompt: str
    duration: float = 4.0
    camera: Optional[str] = None
    motion: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Scene:
    id: str
    title: str
    goal: str = ""
    emotion: str = ""
    shots: List[Shot] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Movie:
    id: str
    title: str
    scenes: List[Scene] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def shots(self) -> List[Shot]:
        return [shot for scene in self.scenes for shot in scene.shots]
