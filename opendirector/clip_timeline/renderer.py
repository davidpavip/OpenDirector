from __future__ import annotations

from pathlib import Path

from opendirector.clip_timeline.models import ClipTimeline
from opendirector.core.timeline_event import TimelineEvent
from opendirector.core.track import Track

TRACK_HEADINGS = {
    Track.VIDEO: "Video",
    Track.NATIVE_AUDIO: "Native Audio",
    Track.DIALOGUE: "Dialogue",
    Track.NARRATION: "Narration",
    Track.MUSIC: "Music",
    Track.AMBIENCE: "Ambience",
    Track.FOLEY: "Foley",
    Track.SOUND_EFFECT: "Sound Effects",
    Track.SUBTITLE: "Subtitles",
}


class ClipTimelineMarkdownRenderer:
    """Render ClipTimeline as filmmaker-editable Markdown."""

    TRACK_ORDER = (
        Track.VIDEO,
        Track.NATIVE_AUDIO,
        Track.DIALOGUE,
        Track.NARRATION,
        Track.MUSIC,
        Track.AMBIENCE,
        Track.FOLEY,
        Track.SOUND_EFFECT,
        Track.SUBTITLE,
    )

    def render(
        self,
        timeline: ClipTimeline,
        production_root: Path | None = None,
    ) -> str:
        source_clip = self._display_path(
            timeline.source_clip.location,
            production_root,
        )

        lines: list[str] = [
            "---",
            "artifact: clip-timeline",
            f"scene: {timeline.scene_id}",
            f"shot: {timeline.shot_id}",
            f"status: {timeline.status}",
            "editable_by: filmmaker",
            f"clip: {source_clip}",
            ("duration: " f"{timeline.duration_timestamp}"),
            "---",
            "",
            f"# {timeline.shot_id} — Clip Timeline",
            "",
            "## Clip",
            "",
            f"- Source: {source_clip}",
            ("- Duration: " f"{timeline.duration_timestamp}"),
            ("- Provider: " f"{timeline.metadata.get('provider_id', 'Unknown')}"),
            (
                "- Native Audio: "
                f"{'Yes' if timeline.metadata.get('has_audio') else 'No'}"
            ),
            (
                "- Audio Baked In: "
                f"{'Yes' if timeline.metadata.get('audio_baked_in') else 'No'}"
            ),
            "",
        ]

        for track in self.TRACK_ORDER:
            lines.extend(
                self._render_track(
                    timeline=timeline,
                    track=track,
                    production_root=production_root,
                )
            )

        lines.extend(
            [
                "## Filmmaker Notes",
                "",
                "None.",
                "",
            ]
        )

        return "\n".join(lines).rstrip() + "\n"

    def _render_track(
        self,
        timeline: ClipTimeline,
        track: Track,
        production_root: Path | None,
    ) -> list[str]:
        lines = [
            f"## {TRACK_HEADINGS[track]}",
            "",
        ]

        events = timeline.by_track(track)

        if not events:
            lines.extend(["None planned.", ""])
            return lines

        for event in events:
            lines.extend(
                self._render_event(
                    event,
                    production_root,
                )
            )

        return lines

    def _render_event(
        self,
        event: TimelineEvent,
        production_root: Path | None,
    ) -> list[str]:
        lines = [
            f"### {event.start} --> {event.end}",
            "",
        ]

        speaker = event.metadata.get("speaker")

        if speaker:
            lines.extend(
                [
                    f"**Speaker:** {speaker}",
                    "",
                ]
            )

        description = event.metadata.get("description") or event.metadata.get("text")

        if description:
            lines.extend(
                [
                    str(description),
                    "",
                ]
            )

        language = event.metadata.get("language")

        if language:
            lines.append(f"- Language: {language}")

        artifact_path = event.metadata.get("artifact_path")

        if artifact_path:
            displayed = self._display_path(
                Path(str(artifact_path)),
                production_root,
            )
            lines.append(f"- Artifact: {displayed}")
        else:
            lines.append("- Artifact: pending")

        reserved = {
            "artifact_path",
            "description",
            "text",
            "speaker",
            "language",
        }

        for key, value in event.metadata.items():
            if key in reserved:
                continue

            label = key.replace("_", " ").title()
            lines.append(f"- {label}: {value}")

        lines.append("")

        return lines

    @staticmethod
    def _display_path(
        path: Path,
        production_root: Path | None,
    ) -> str:
        resolved = path.resolve()

        if production_root is not None:
            try:
                return str(resolved.relative_to(production_root.resolve()))
            except ValueError:
                pass

        return str(path)
