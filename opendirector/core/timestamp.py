"""SRT-style timestamp primitive for OpenDirector.

Canonical public format:

    HH:MM:SS,mmm

Example:

    00:01:13,500

Internally, Timestamp stores integer milliseconds.
No floating-point time is used inside the core timeline.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Union


TimestampInput = Union["Timestamp", str, int, float]


_SRT_RE = re.compile(
    r"^(?P<hours>\d{2,}):(?P<minutes>[0-5]\d):(?P<seconds>[0-5]\d)[,.](?P<milliseconds>\d{1,3})$"
)


@dataclass(frozen=True, order=True)
class Timestamp:
    """Immutable millisecond-accurate timestamp.

    Public display uses SRT format: HH:MM:SS,mmm.
    Internally stores integer milliseconds.
    """

    milliseconds: int

    def __post_init__(self) -> None:
        if self.milliseconds < 0:
            raise ValueError("Timestamp cannot be negative")

    @classmethod
    def parse(cls, value: TimestampInput) -> "Timestamp":
        """Create a Timestamp from Timestamp, SRT string, seconds, or milliseconds.

        Accepted inputs:
            Timestamp("00:01:13,500") via parse
            "00:01:13,500"
            "00:01:13.500"
            "73.5"       # seconds
            73.5         # seconds
            73500        # milliseconds if int
        """

        if isinstance(value, Timestamp):
            return value

        if isinstance(value, int):
            return cls(value)

        if isinstance(value, float):
            return cls(round(value * 1000))

        if not isinstance(value, str):
            raise TypeError(f"Unsupported Timestamp input: {type(value)!r}")

        text = value.strip()

        match = _SRT_RE.match(text)
        if match:
            hours = int(match.group("hours"))
            minutes = int(match.group("minutes"))
            seconds = int(match.group("seconds"))
            ms_text = match.group("milliseconds").ljust(3, "0")
            milliseconds = int(ms_text)

            total = (
                hours * 3_600_000
                + minutes * 60_000
                + seconds * 1_000
                + milliseconds
            )
            return cls(total)

        # Numeric string means seconds.
        try:
            seconds_float = float(text)
        except ValueError as exc:
            raise ValueError(
                "Timestamp must be SRT-style HH:MM:SS,mmm or numeric seconds"
            ) from exc

        if seconds_float < 0:
            raise ValueError("Timestamp cannot be negative")

        return cls(round(seconds_float * 1000))

    @classmethod
    def zero(cls) -> "Timestamp":
        return cls(0)

    def to_seconds(self) -> float:
        return self.milliseconds / 1000

    def to_srt(self) -> str:
        total = self.milliseconds

        hours, remainder = divmod(total, 3_600_000)
        minutes, remainder = divmod(remainder, 60_000)
        seconds, milliseconds = divmod(remainder, 1_000)

        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    def __str__(self) -> str:
        return self.to_srt()

    def __add__(self, other: TimestampInput) -> "Timestamp":
        other_ts = Timestamp.parse(other)
        return Timestamp(self.milliseconds + other_ts.milliseconds)

    def __sub__(self, other: TimestampInput) -> "Timestamp":
        other_ts = Timestamp.parse(other)
        return Timestamp(self.milliseconds - other_ts.milliseconds)
