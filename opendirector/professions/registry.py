from __future__ import annotations

from collections.abc import Iterator

from opendirector.professions.base import Profession


class ProfessionRegistry:
    """Registry of professional identities available to the Studio."""

    def __init__(self) -> None:
        self._professions: dict[str, Profession] = {}

    def register(
        self,
        profession: Profession,
    ) -> Profession:
        key = self._normalize(profession.name)

        if key in self._professions:
            raise ValueError(f"Profession already registered: {profession.name}")

        self._professions[key] = profession
        return profession

    def get(self, name: str) -> Profession:
        key = self._normalize(name)

        try:
            return self._professions[key]
        except KeyError as exc:
            raise KeyError(f"Profession not registered: {name}") from exc

    def contains(self, name: str) -> bool:
        return self._normalize(name) in self._professions

    def all(self) -> list[Profession]:
        return list(self._professions.values())

    def __len__(self) -> int:
        return len(self._professions)

    def __iter__(self) -> Iterator[Profession]:
        return iter(self._professions.values())

    def _normalize(self, name: str) -> str:
        normalized = name.strip().lower()

        if not normalized:
            raise ValueError("Profession name cannot be empty")

        return normalized
