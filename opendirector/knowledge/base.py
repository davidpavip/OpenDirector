from __future__ import annotations

from collections.abc import Iterable

from opendirector.knowledge.models import (
    KnowledgeKind,
    KnowledgeRecord,
)


class KnowledgeBase:
    """Persistent conceptual memory of the Studio.

    This first implementation is in-memory only. It defines ownership,
    precedence, filtering, and conflict resolution.
    """

    def __init__(self) -> None:
        self._records: dict[str, KnowledgeRecord] = {}

    def add(self, record: KnowledgeRecord) -> KnowledgeRecord:
        if record.id in self._records:
            raise ValueError(f"Knowledge record already exists: {record.id}")

        self._records[record.id] = record
        return record

    def extend(
        self,
        records: Iterable[KnowledgeRecord],
    ) -> list[KnowledgeRecord]:
        return [self.add(record) for record in records]

    def get(self, record_id: str) -> KnowledgeRecord:
        try:
            return self._records[record_id]
        except KeyError as exc:
            raise KeyError(f"Knowledge record not found: {record_id}") from exc

    def all(self) -> list[KnowledgeRecord]:
        return list(self._records.values())

    def by_kind(self, kind: KnowledgeKind) -> list[KnowledgeRecord]:
        return [record for record in self._records.values() if record.kind is kind]

    def active(self) -> list[KnowledgeRecord]:
        return [record for record in self._records.values() if record.is_active]

    def for_subject(self, subject: str) -> list[KnowledgeRecord]:
        """Return relevant records ordered by governing priority."""

        records = [record for record in self.active() if record.applies_to(subject)]

        return sorted(
            records,
            key=lambda record: (
                -record.priority,
                -record.confidence,
                record.created_at,
            ),
        )

    def governing_values(
        self,
        subject: str,
    ) -> list[KnowledgeRecord]:
        return [
            record
            for record in self.for_subject(subject)
            if record.kind is KnowledgeKind.VALUE
        ]

    def resolve(
        self,
        subject: str,
    ) -> list[KnowledgeRecord]:
        """Return knowledge in decision precedence order.

        Values are always first, followed by Education, then Experience.
        This does not merge or reinterpret statements yet.
        """

        return self.for_subject(subject)

    def __len__(self) -> int:
        return len(self._records)
