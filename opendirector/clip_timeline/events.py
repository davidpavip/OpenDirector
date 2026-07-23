from __future__ import annotations

from opendirector.core.timeline import TimelineEvent


class ClipMediaEvent(TimelineEvent):
    """Video or embedded native-audio media on a clip timeline."""

    def __init__(
        self,
        start: float,
        duration: float,
        track: str,
        artifact_path: str,
        description: str = "",
        **metadata,
    ) -> None:
        super().__init__(
            start=start,
            duration=duration,
            track=track,
            event_type="clip_media",
            metadata={
                "artifact_path": artifact_path,
                "description": description,
                **metadata,
            },
        )


class DialogueEvent(TimelineEvent):
    """Planned, native, replacement, or dubbed dialogue."""

    def __init__(
        self,
        start: float,
        duration: float,
        text: str,
        speaker: str = "",
        language: str = "",
        delivery: str = "",
        **metadata,
    ) -> None:
        super().__init__(
            start=start,
            duration=duration,
            track="dialogue",
            event_type="dialogue",
            metadata={
                "text": text,
                "speaker": speaker,
                "language": language,
                "delivery": delivery,
                **metadata,
            },
        )


class NarrationEvent(TimelineEvent):
    """Narration or voice-over planned for the clip."""

    def __init__(
        self,
        start: float,
        duration: float,
        text: str,
        language: str = "",
        **metadata,
    ) -> None:
        super().__init__(
            start=start,
            duration=duration,
            track="narration",
            event_type="narration",
            metadata={
                "text": text,
                "language": language,
                **metadata,
            },
        )


class SoundDirectionEvent(TimelineEvent):
    """Music, ambience, Foley, or sound-effect direction."""

    def __init__(
        self,
        start: float,
        duration: float,
        track: str,
        description: str,
        **metadata,
    ) -> None:
        if track not in {
            "music",
            "ambience",
            "sound_effect",
            "foley",
        }:
            raise ValueError(f"Unsupported sound track: {track}")

        super().__init__(
            start=start,
            duration=duration,
            track=track,
            event_type="sound_direction",
            metadata={
                "description": description,
                **metadata,
            },
        )


class SubtitleEvent(TimelineEvent):
    """One timed subtitle entry."""

    def __init__(
        self,
        start: float,
        duration: float,
        text: str,
        language: str,
        **metadata,
    ) -> None:
        super().__init__(
            start=start,
            duration=duration,
            track="subtitle",
            event_type="subtitle",
            metadata={
                "text": text,
                "language": language,
                **metadata,
            },
        )
