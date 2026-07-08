from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


class CandidateStatus(StrEnum):
    NEW = "new"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


@dataclass
class ReviewerScore:
    reviewer: str
    category: str
    score: int
    confidence: float = 1.0
    comment: str = ""

    def __post_init__(self) -> None:
        if not 0 <= self.score <= 100:
            raise ValueError("score must be between 0 and 100")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")


@dataclass
class Candidate:
    candidate_type: str
    title: str
    payload: dict[str, Any] = field(default_factory=dict)
    created_by: str = "unknown"
    id: str = field(default_factory=lambda: str(uuid4()))
    status: CandidateStatus = CandidateStatus.NEW
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    scores: list[ReviewerScore] = field(default_factory=list)

    def add_score(self, score: ReviewerScore) -> None:
        self.scores.append(score)

    @property
    def average_score(self) -> float:
        if not self.scores:
            return 0.0
        return sum(s.score for s in self.scores) / len(self.scores)

    def approve(self) -> None:
        self.status = CandidateStatus.APPROVED

    def reject(self) -> None:
        self.status = CandidateStatus.REJECTED

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "candidate_type": self.candidate_type,
            "title": self.title,
            "status": self.status.value,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "average_score": self.average_score,
            "payload": self.payload,
            "scores": [s.__dict__ for s in self.scores],
        }


@dataclass
class CandidateSet:
    purpose: str
    id: str = field(default_factory=lambda: str(uuid4()))
    candidates: list[Candidate] = field(default_factory=list)
    selected_id: str | None = None

    def add(self, candidate: Candidate) -> Candidate:
        self.candidates.append(candidate)
        return candidate

    def select(self, candidate_id: str) -> Candidate:
        candidate = self.get(candidate_id)
        candidate.approve()
        self.selected_id = candidate.id
        return candidate

    def get(self, candidate_id: str) -> Candidate:
        for candidate in self.candidates:
            if candidate.id == candidate_id:
                return candidate
        raise KeyError(f"Candidate not found: {candidate_id}")

    def winner(self) -> Candidate | None:
        if self.selected_id:
            return self.get(self.selected_id)
        if not self.candidates:
            return None
        return max(self.candidates, key=lambda c: c.average_score)

    def ranked(self) -> list[Candidate]:
        return sorted(self.candidates, key=lambda c: c.average_score, reverse=True)
