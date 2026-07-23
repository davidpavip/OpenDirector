from __future__ import annotations

from enum import StrEnum


class Track(StrEnum):
    """Canonical creative and media tracks."""

    STORY = "story"
    VIDEO = "video"

    AUDIO = "audio"
    NATIVE_AUDIO = "native_audio"
    DIALOGUE = "dialogue"
    NARRATION = "narration"
    AMBIENCE = "ambience"
    FOLEY = "foley"
    SOUND_EFFECT = "sound_effect"
    MUSIC = "music"

    SUBTITLE = "subtitle"
    CAMERA = "camera"
    REVIEW = "review"
    NOTES = "notes"
    MARKER = "marker"
