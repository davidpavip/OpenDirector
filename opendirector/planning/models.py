from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class SourceDocument:
    """Canonical UTF-8 Markdown input consumed by OpenDirector."""

    content: str
    title: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError("SourceDocument content cannot be empty")


@dataclass(frozen=True)
class StoryRole:
    """A functional participant in the story world."""

    name: str
    purpose: str = ""
    importance: str = "supporting"
    attributes: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("StoryRole name cannot be empty")


@dataclass(frozen=True)
class Profession:
    """A responsibility required to produce the work."""

    name: str
    responsibilities: tuple[str, ...] = ()
    required_knowledge: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Profession name cannot be empty")


class AssignmentMode(str, Enum):
    HUMAN = "human"
    AI_ASSISTANT = "ai_assistant"
    AI_DELEGATE = "ai_delegate"
    HUMAN_AI = "human_ai"


@dataclass(frozen=True)
class RoleAssignment:
    """Assign a production profession to a human, AI, or both."""

    profession_name: str
    mode: AssignmentMode
    performer: str = ""
    authority_notes: str = ""

    def __post_init__(self) -> None:
        if not self.profession_name.strip():
            raise ValueError("Assignment profession cannot be empty")


class BlueprintStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    SUPERSEDED = "superseded"


@dataclass(frozen=True)
class ProductionBlueprint:
    """Versioned agreement between the filmmaker and the Studio."""

    source: SourceDocument
    version: int = 1
    status: BlueprintStatus = BlueprintStatus.DRAFT

    intent_summary: str = ""
    story_summary: str = ""

    story_roles: tuple[StoryRole, ...] = ()
    professions: tuple[Profession, ...] = ()
    assignments: tuple[RoleAssignment, ...] = ()

    style: dict[str, Any] = field(default_factory=dict)
    constraints: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    approved_by: str | None = None
    approved_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.version < 1:
            raise ValueError("Blueprint version must be >= 1")

    @property
    def is_approved(self) -> bool:
        return self.status is BlueprintStatus.APPROVED

    def approve(self, approved_by: str) -> ProductionBlueprint:
        if self.is_approved:
            raise ValueError("ProductionBlueprint is already approved")

        if not approved_by.strip():
            raise ValueError("Blueprint approver cannot be empty")

        if not self.intent_summary.strip():
            raise ValueError("Blueprint requires an intent before approval")

        if not self.story_summary.strip():
            raise ValueError("Blueprint requires a story before approval")

        return replace(
            self,
            status=BlueprintStatus.APPROVED,
            approved_by=approved_by,
            approved_at=datetime.now(timezone.utc),
        )

    def revise(self) -> ProductionBlueprint:
        """Create a new editable version while preserving approved history."""

        return replace(
            self,
            version=self.version + 1,
            status=BlueprintStatus.DRAFT,
            approved_by=None,
            approved_at=None,
        )
