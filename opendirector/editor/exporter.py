from __future__ import annotations

from pathlib import Path
import subprocess
from typing import List

from opendirector.core.project import Project
from opendirector.core.timeline import Timeline


def export_simple_concat(project: Project, timeline: Timeline, output: str | Path | None = None) -> Path:
    """Export video_clip events in timeline order using ffmpeg concat.

    This is intentionally simple. It ignores trims/transitions for now and gives
    us a reliable first director's cut from Timeline events.
    """
    clips: List[Path] = []
    for event in timeline.by_track("video"):
        if event.kind != "video_clip" or not event.asset:
            continue
        clip = project.path(event.asset)
        if not clip.exists():
            # Allow legacy project layout where video_file starts with videos/.
            clip = project.path("assets", event.asset)
        if not clip.exists():
            raise FileNotFoundError(f"Missing clip for timeline event {event.id}: {event.asset}")
        clips.append(clip)

    if not clips:
        raise ValueError("Timeline contains no video_clip events")

    out = Path(output) if output else project.path("export", "director_cut_v1.mp4")
    if not out.is_absolute():
        out = project.path(str(out))
    out.parent.mkdir(parents=True, exist_ok=True)

    list_file = out.parent / "concat_list.txt"
    list_file.write_text("".join(f"file '{clip.resolve()}'\n" for clip in clips), encoding="utf-8")

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(out),
    ], check=True)
    return out
