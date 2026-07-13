from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GenerationResult:
    """Summary of one completed evolutionary generation."""

    generation: int
    mode: str
    candidate_set_id: str
    selected_candidate_id: str
    completed_operators: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "generation": self.generation,
            "mode": self.mode,
            "candidate_set_id": self.candidate_set_id,
            "selected_candidate_id": self.selected_candidate_id,
            "completed_operators": list(self.completed_operators),
        }
