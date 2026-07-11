from __future__ import annotations

from abc import ABC, abstractmethod

from opendirector.creative.context import CreativeContext


class CrewMember(ABC):
    """A creative role working inside the Studio."""

    role: str = "crew_member"
    name: str = "Unnamed Crew Member"

    @abstractmethod
    async def perform(self, context: CreativeContext) -> CreativeContext:
        """Perform this crew member's work."""
        raise NotImplementedError
