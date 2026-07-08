from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from .models import Shot
from .project import Project


class Renderer(ABC):
    """Renderer plugin interface.

    All video backends, LTX, Veo, Runway, local GPU, must implement this.
    """

    @abstractmethod
    def render_shot(self, project: Project, shot: Shot, overwrite: bool = False) -> Path:
        raise NotImplementedError
