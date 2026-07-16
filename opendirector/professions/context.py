from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProfessionContext:
    """Provider-neutral context available to a profession.

    This will eventually become a view of StudioContext.
    """

    values: tuple[str, ...] = ()
    education: tuple[str, ...] = ()
    experience: tuple[str, ...] = ()

    source: str = ""
    production: str = ""
    conversation: str = ""

    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Values are intentionally always present as a section, even when
        # the current Studio has not defined any explicit values yet.
        if self.values is None:
            raise ValueError("ProfessionContext values cannot be None")
