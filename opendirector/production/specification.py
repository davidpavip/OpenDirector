from __future__ import annotations

from dataclasses import dataclass, field
import re


@dataclass(frozen=True)
class ProductionSpecification:
    """Production-wide requirements understood from source.md.

    These values are defaults and constraints shared by planning
    and later creative operators.
    """

    creative_profile: str = "movie"
    distribution: str = ""
    preferred_orientation: str = "landscape"

    target_duration_seconds: int | None = None

    narration_language: str = "English"
    subtitle_languages: tuple[str, ...] = ("English",)

    visual_style: str = ""
    target_audience: str = ""
    tone: str = ""
    notes: str = ""

    @property
    def aspect_ratio(self) -> str:
        orientation = self.preferred_orientation.casefold()

        if orientation == "portrait":
            return "9:16"

        if orientation == "square":
            return "1:1"

        return "16:9"

    def to_prompt_text(self) -> str:
        """Return a provider-neutral description for AI operators."""

        duration = (
            f"{self.target_duration_seconds} seconds"
            if self.target_duration_seconds is not None
            else "Not specified"
        )

        subtitle_languages = ", ".join(self.subtitle_languages)

        return "\n".join(
            [
                f"Creative profile: {self.creative_profile}",
                f"Distribution: {self.distribution or 'Not specified'}",
                f"Orientation: {self.preferred_orientation}",
                f"Aspect ratio: {self.aspect_ratio}",
                f"Target duration: {duration}",
                f"Narration language: {self.narration_language}",
                f"Subtitle languages: {subtitle_languages}",
                f"Visual style: {self.visual_style or 'Not specified'}",
                f"Target audience: {self.target_audience or 'Not specified'}",
                f"Tone: {self.tone or 'Not specified'}",
                f"Notes: {self.notes or 'None'}",
            ]
        )


@dataclass(frozen=True)
class ProductionSpecificationParser:
    """Extract a practical specification from natural-language source text."""

    default_specification: ProductionSpecification = field(
        default_factory=ProductionSpecification
    )

    def parse(self, source: str) -> ProductionSpecification:
        if not source.strip():
            return self.default_specification

        return ProductionSpecification(
            creative_profile=self._creative_profile(source),
            distribution=self._distribution(source),
            preferred_orientation=self._orientation(source),
            target_duration_seconds=self._duration(source),
            narration_language=self._narration_language(source),
            subtitle_languages=self._subtitle_languages(source),
            visual_style=self._visual_style(source),
            target_audience=self._target_audience(source),
            tone=self._tone(source),
            notes="",
        )

    def _creative_profile(self, source: str) -> str:
        lowered = source.casefold()

        profiles = (
            ("audiobook", "audiobook"),
            ("audio book", "audiobook"),
            ("documentary", "documentary"),
            ("news", "news"),
            ("podcast", "podcast"),
            ("tutorial", "tutorial"),
            ("interview", "interview"),
            ("movie", "movie"),
            ("film", "movie"),
            ("video", "video"),
        )

        for phrase, value in profiles:
            if phrase in lowered:
                return value

        return self.default_specification.creative_profile

    def _distribution(self, source: str) -> str:
        lowered = source.casefold()

        platforms = (
            ("youtube shorts", "youtube_shorts"),
            ("youtube short", "youtube_shorts"),
            ("instagram reels", "instagram_reels"),
            ("instagram reel", "instagram_reels"),
            ("tiktok", "tiktok"),
            ("youtube", "youtube"),
            ("instagram", "instagram"),
            ("facebook", "facebook"),
        )

        for phrase, value in platforms:
            if phrase in lowered:
                return value

        # Match X carefully so ordinary words containing x are ignored.
        if re.search(
            r"\b(?:for|on|to)\s+x\b",
            source,
            flags=re.IGNORECASE,
        ):
            return "x"

        return self.default_specification.distribution

    def _orientation(self, source: str) -> str:
        lowered = source.casefold()

        if "portrait" in lowered or "vertical" in lowered:
            return "portrait"

        if "square" in lowered:
            return "square"

        if "landscape" in lowered or "horizontal" in lowered:
            return "landscape"

        return self.default_specification.preferred_orientation

    def _duration(self, source: str) -> int | None:
        seconds_match = re.search(
            r"\b(\d{1,5})[\s-]*" r"(?:second|seconds|sec|secs)\b",
            source,
            flags=re.IGNORECASE,
        )

        if seconds_match:
            return int(seconds_match.group(1))

        minutes_match = re.search(
            r"\b(\d{1,4})[\s-]*" r"(?:minute|minutes|min|mins)\b",
            source,
            flags=re.IGNORECASE,
        )

        if minutes_match:
            return int(minutes_match.group(1)) * 60

        return self.default_specification.target_duration_seconds

    def _narration_language(self, source: str) -> str:
        match = re.search(
            r"narration(?:\s+language)?\s*(?:is|:|in)?\s*"
            r"([A-Za-z][A-Za-z -]{1,40})",
            source,
            flags=re.IGNORECASE,
        )

        if not match:
            match = re.search(
                r"narrat(?:e|ed|ion)\s+in\s+" r"([A-Za-z][A-Za-z -]{1,40})",
                source,
                flags=re.IGNORECASE,
            )

        if not match:
            return self.default_specification.narration_language

        return self._clean_language(match.group(1))

    def _subtitle_languages(
        self,
        source: str,
    ) -> tuple[str, ...]:
        match = re.search(
            r"subtitle(?:s|\s+languages?)?\s*" r"(?:are|:|in)?\s*([^\n.]+)",
            source,
            flags=re.IGNORECASE,
        )

        if not match:
            return self.default_specification.subtitle_languages

        text = match.group(1)
        text = re.sub(
            r"\b(?:and|plus)\b",
            ",",
            text,
            flags=re.IGNORECASE,
        )

        languages = tuple(
            self._clean_language(value) for value in text.split(",") if value.strip()
        )

        return languages or self.default_specification.subtitle_languages

    def _visual_style(self, source: str) -> str:
        patterns = (
            r"visual style\s*(?:is|:)?\s*([^\n.]+)",
            r"style\s*(?:is|:)?\s*([^\n.]+)",
            r"([A-Za-z0-9 -]+(?:style|animation))",
        )

        return self._first_match(source, patterns)

    def _target_audience(self, source: str) -> str:
        patterns = (
            r"target audience\s*(?:is|:)?\s*([^\n.]+)",
            r"audience\s*(?:is|:)?\s*([^\n.]+)",
            r"for\s+(families|children|adults|teenagers|teens)\b",
        )

        return self._first_match(source, patterns)

    def _tone(self, source: str) -> str:
        patterns = (
            r"tone\s*(?:should\s+be|is|:|of)?\s*([^\n.]+)",
            r"(?:feel|feels|feeling)\s+([^\n.]+)",
        )

        return self._first_match(source, patterns)

    @staticmethod
    def _first_match(
        source: str,
        patterns: tuple[str, ...],
    ) -> str:
        for pattern in patterns:
            match = re.search(
                pattern,
                source,
                flags=re.IGNORECASE,
            )

            if match:
                return match.group(1).strip(" ,:-")

        return ""

    @staticmethod
    def _clean_language(value: str) -> str:
        cleaned = re.split(
            r"\b(?:with|for|using|and generate|subtitles?)\b",
            value,
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0]

        return cleaned.strip(" ,:-").title()
