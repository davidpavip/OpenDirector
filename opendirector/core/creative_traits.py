from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any


@dataclass(frozen=True)
class CreativeTraits:
    """Structured, inheritable characteristics of a creative candidate."""

    camera: str = ""
    lighting: str = ""
    emotion: str = ""
    pacing: str = ""
    composition: str = ""
    performance: str = ""
    sound: str = ""
    style: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def evolve(self, **changes: Any) -> "CreativeTraits":
        """Create a modified trait set without changing the parent."""
        return replace(self, **changes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "camera": self.camera,
            "lighting": self.lighting,
            "emotion": self.emotion,
            "pacing": self.pacing,
            "composition": self.composition,
            "performance": self.performance,
            "sound": self.sound,
            "style": self.style,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CreativeTraits":
        return cls(
            camera=str(data.get("camera", "")),
            lighting=str(data.get("lighting", "")),
            emotion=str(data.get("emotion", "")),
            pacing=str(data.get("pacing", "")),
            composition=str(data.get("composition", "")),
            performance=str(data.get("performance", "")),
            sound=str(data.get("sound", "")),
            style=str(data.get("style", "")),
            metadata=dict(data.get("metadata", {})),
        )
