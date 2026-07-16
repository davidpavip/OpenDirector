from __future__ import annotations

from abc import ABC, abstractmethod

from opendirector.professions import Assignment, ProfessionContext
from opendirector.thinking.models import Understanding


class UnderstandingPolicy(ABC):
    """Strategy used to understand one professional assignment."""

    @abstractmethod
    async def understand(
        self,
        assignment: Assignment,
        context: ProfessionContext,
    ) -> Understanding:
        raise NotImplementedError


class DeterministicUnderstandingPolicy(UnderstandingPolicy):
    """Initial provider-free understanding policy.

    It converts explicit assignment and context information into a
    structured Understanding artifact. It does not invent story content.
    """

    async def understand(
        self,
        assignment: Assignment,
        context: ProfessionContext,
    ) -> Understanding:
        constraints = self._unique(
            assignment.constraints
            + self._metadata_strings(
                assignment.metadata,
                "constraints",
            )
        )

        goals = self._unique(
            self._metadata_strings(
                assignment.metadata,
                "goals",
            )
        )

        audience = self._unique(
            self._metadata_strings(
                assignment.metadata,
                "audience",
            )
        )

        assumptions = self._unique(
            self._metadata_strings(
                assignment.metadata,
                "assumptions",
            )
        )

        unknowns = list(
            self._metadata_strings(
                assignment.metadata,
                "unknowns",
            )
        )

        risks = list(
            self._metadata_strings(
                assignment.metadata,
                "risks",
            )
        )

        if not context.source.strip():
            unknowns.append("No normalized source context was supplied.")

        if not assignment.deliverable_type.strip():
            unknowns.append("The expected deliverable type is not specified.")

        if not context.values:
            risks.append("No explicit Studio values were supplied.")

        evidence = self._build_evidence(
            assignment=assignment,
            context=context,
        )

        confidence = self._calculate_confidence(
            assignment=assignment,
            context=context,
            unknowns=tuple(unknowns),
        )

        return Understanding(
            intent=assignment.objective.strip(),
            goals=goals,
            audience=audience,
            constraints=constraints,
            assumptions=assumptions,
            unknowns=self._unique(tuple(unknowns)),
            risks=self._unique(tuple(risks)),
            evidence=evidence,
            confidence=confidence,
            metadata={
                "profession": assignment.profession,
                "assignment_id": assignment.id,
                "policy": self.__class__.__name__,
                "values_loaded": len(context.values),
                "education_loaded": len(context.education),
                "experience_loaded": len(context.experience),
            },
        )

    def _build_evidence(
        self,
        assignment: Assignment,
        context: ProfessionContext,
    ) -> tuple[str, ...]:
        evidence: list[str] = [
            f"Assignment objective: {assignment.objective.strip()}",
        ]

        if context.source.strip():
            evidence.append("Normalized source context is available.")

        if context.production.strip():
            evidence.append("Production context is available.")

        if context.conversation.strip():
            evidence.append("Conversation context is available.")

        if context.values:
            evidence.append(f"{len(context.values)} governing value(s) loaded.")

        if context.education:
            evidence.append(f"{len(context.education)} education record(s) loaded.")

        if context.experience:
            evidence.append(f"{len(context.experience)} experience record(s) loaded.")

        return tuple(evidence)

    def _calculate_confidence(
        self,
        assignment: Assignment,
        context: ProfessionContext,
        unknowns: tuple[str, ...],
    ) -> float:
        confidence = 0.45

        if assignment.objective.strip():
            confidence += 0.15

        if assignment.deliverable_type.strip():
            confidence += 0.10

        if context.source.strip():
            confidence += 0.15

        if context.values:
            confidence += 0.05

        if context.production.strip():
            confidence += 0.05

        confidence -= min(0.30, len(unknowns) * 0.10)

        return max(0.0, min(1.0, round(confidence, 2)))

    def _metadata_strings(
        self,
        metadata: dict[str, object],
        key: str,
    ) -> tuple[str, ...]:
        value = metadata.get(key)

        if value is None:
            return ()

        if isinstance(value, str):
            normalized = value.strip()
            return (normalized,) if normalized else ()

        if isinstance(value, (list, tuple, set)):
            result: list[str] = []

            for item in value:
                normalized = str(item).strip()
                if normalized:
                    result.append(normalized)

            return tuple(result)

        normalized = str(value).strip()
        return (normalized,) if normalized else ()

    def _unique(
        self,
        values: tuple[str, ...],
    ) -> tuple[str, ...]:
        result: list[str] = []
        seen: set[str] = set()

        for value in values:
            normalized = value.strip()
            key = normalized.lower()

            if normalized and key not in seen:
                result.append(normalized)
                seen.add(key)

        return tuple(result)
