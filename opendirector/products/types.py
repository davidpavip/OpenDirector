from __future__ import annotations

from dataclasses import dataclass

from opendirector.products.models import CreativeProduct


@dataclass(frozen=True)
class SketchProduct(CreativeProduct):
    """Visual planning product for one scene or shot."""


@dataclass(frozen=True)
class ImageProduct(CreativeProduct):
    """Still-image product."""


@dataclass(frozen=True)
class AnimationProduct(CreativeProduct):
    """Moving-image product."""

    duration_seconds: float = 0.0
    fps: float | None = None

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.duration_seconds < 0:
            raise ValueError("AnimationProduct duration cannot be negative")

        if self.fps is not None and self.fps <= 0:
            raise ValueError("AnimationProduct fps must be greater than zero")


@dataclass(frozen=True)
class AudioProduct(CreativeProduct):
    """Audio product such as voice, music, or sound design."""

    duration_seconds: float = 0.0

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.duration_seconds < 0:
            raise ValueError("AudioProduct duration cannot be negative")


@dataclass(frozen=True)
class EditProduct(CreativeProduct):
    """Assembled scene or production edit."""


@dataclass(frozen=True)
class ReviewProduct(CreativeProduct):
    """Review report or structured evaluation product."""

    score: float | None = None

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.score is not None and not 0.0 <= self.score <= 1.0:
            raise ValueError("ReviewProduct score must be between 0 and 1")
