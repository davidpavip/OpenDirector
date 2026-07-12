from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class LanguageRequest:
    system_instruction: str
    user_message: str
    context: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LanguageResult:
    text: str
    model: str
    provider_id: str
    metadata: dict[str, Any] = field(default_factory=dict)


class LanguageProvider(Protocol):
    provider_id: str
    display_name: str

    async def generate(self, request: LanguageRequest) -> LanguageResult: ...
