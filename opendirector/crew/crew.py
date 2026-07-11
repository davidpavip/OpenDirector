from __future__ import annotations

from opendirector.crew.member import CrewMember


class Crew:
    """Collection of creative crew members owned by a Studio."""

    def __init__(self) -> None:
        self._members: dict[str, CrewMember] = {}

    def add(self, member: CrewMember) -> CrewMember:
        if member.role in self._members:
            raise ValueError(f"Crew role already filled: {member.role}")

        self._members[member.role] = member
        return member

    def replace(self, member: CrewMember) -> CrewMember:
        self._members[member.role] = member
        return member

    def get(self, role: str) -> CrewMember:
        try:
            return self._members[role]
        except KeyError as exc:
            raise KeyError(f"No crew member assigned to role: {role}") from exc

    def has(self, role: str) -> bool:
        return role in self._members

    def remove(self, role: str) -> CrewMember:
        try:
            return self._members.pop(role)
        except KeyError as exc:
            raise KeyError(f"No crew member assigned to role: {role}") from exc

    def all(self) -> list[CrewMember]:
        return list(self._members.values())

    def __getitem__(self, role: str) -> CrewMember:
        return self.get(role)

    def __len__(self) -> int:
        return len(self._members)
