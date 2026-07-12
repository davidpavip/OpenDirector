from __future__ import annotations

from typing import Any


class ProviderRegistry:
    """Studio-level registry for technical capability providers."""

    def __init__(self) -> None:
        self._providers: dict[str, Any] = {}

    def register(self, provider: Any) -> Any:
        provider_id = provider.provider_id

        if provider_id in self._providers:
            raise ValueError(f"Provider already registered: {provider_id}")

        self._providers[provider_id] = provider
        return provider

    def replace(self, provider: Any) -> Any:
        self._providers[provider.provider_id] = provider
        return provider

    def get(self, provider_id: str) -> Any:
        try:
            return self._providers[provider_id]
        except KeyError as exc:
            raise KeyError(f"Provider not registered: {provider_id}") from exc

    def has(self, provider_id: str) -> bool:
        return provider_id in self._providers

    def all(self) -> list[Any]:
        return list(self._providers.values())

    def __len__(self) -> int:
        return len(self._providers)
