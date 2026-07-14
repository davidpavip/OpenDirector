from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

from opendirector.planning.models import (
    Profession,
    ProductionBlueprint,
    StoryRole,
)


@dataclass(frozen=True)
class BlueprintSeed:
    """One initial interpretation of a production source."""

    title: str
    intent_summary: str
    story_summary: str

    story_roles: tuple[StoryRole, ...] = ()
    professions: tuple[Profession, ...] = ()
    style: dict[str, Any] = field(default_factory=dict)
    constraints: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("BlueprintSeed title cannot be empty")

        if not self.intent_summary.strip():
            raise ValueError("BlueprintSeed intent cannot be empty")

        if not self.story_summary.strip():
            raise ValueError("BlueprintSeed story cannot be empty")

    def create_blueprint(
        self,
        template: ProductionBlueprint,
    ) -> ProductionBlueprint:
        return replace(
            template,
            intent_summary=self.intent_summary,
            story_summary=self.story_summary,
            story_roles=self.story_roles,
            professions=self.professions,
            style=dict(self.style),
            constraints=self.constraints,
            metadata={
                **template.metadata,
                "blueprint_candidate_title": self.title,
                "evolution_operation": "seed",
                "generation": 1,
            },
        )


@dataclass(frozen=True)
class BlueprintMutation:
    """A controlled change applied to a selected blueprint."""

    name: str

    intent_summary: str | None = None
    story_summary: str | None = None

    add_story_roles: tuple[StoryRole, ...] = ()
    remove_story_roles: tuple[str, ...] = ()

    add_professions: tuple[Profession, ...] = ()
    remove_professions: tuple[str, ...] = ()

    style_changes: dict[str, Any] = field(default_factory=dict)
    add_constraints: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("BlueprintMutation name cannot be empty")

    def apply(
        self,
        parent: ProductionBlueprint,
        generation: int,
    ) -> ProductionBlueprint:
        removed_role_names = {name.strip().lower() for name in self.remove_story_roles}
        roles = tuple(
            role
            for role in parent.story_roles
            if role.name.strip().lower() not in removed_role_names
        )
        roles = self._append_unique_roles(
            roles,
            self.add_story_roles,
        )

        removed_profession_names = {
            name.strip().lower() for name in self.remove_professions
        }
        professions = tuple(
            profession
            for profession in parent.professions
            if profession.name.strip().lower() not in removed_profession_names
        )
        professions = self._append_unique_professions(
            professions,
            self.add_professions,
        )

        return replace(
            parent,
            intent_summary=(
                self.intent_summary
                if self.intent_summary is not None
                else parent.intent_summary
            ),
            story_summary=(
                self.story_summary
                if self.story_summary is not None
                else parent.story_summary
            ),
            story_roles=roles,
            professions=professions,
            style={
                **parent.style,
                **self.style_changes,
            },
            constraints=tuple(dict.fromkeys(parent.constraints + self.add_constraints)),
            metadata={
                **parent.metadata,
                "blueprint_candidate_title": self.name,
                "evolution_operation": "mutation",
                "mutation_name": self.name,
                "generation": generation,
            },
        )

    def _append_unique_roles(
        self,
        existing: tuple[StoryRole, ...],
        additions: tuple[StoryRole, ...],
    ) -> tuple[StoryRole, ...]:
        result = list(existing)
        known = {role.name.strip().lower() for role in result}

        for role in additions:
            key = role.name.strip().lower()
            if key not in known:
                result.append(role)
                known.add(key)

        return tuple(result)

    def _append_unique_professions(
        self,
        existing: tuple[Profession, ...],
        additions: tuple[Profession, ...],
    ) -> tuple[Profession, ...]:
        result = list(existing)
        known = {profession.name.strip().lower() for profession in result}

        for profession in additions:
            key = profession.name.strip().lower()
            if key not in known:
                result.append(profession)
                known.add(key)

        return tuple(result)
