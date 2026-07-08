from __future__ import annotations

from pathlib import Path
import typer
from rich import print

from opendirector.core.event_bus import EventBus
from opendirector.core.timeline import Timeline, StoryBeatEvent, VideoClipEvent, ReviewEvent
from opendirector.diary.production_diary import ProductionDiary

app = typer.Typer()
diary_app = typer.Typer()
app.add_typer(diary_app, name="diary")


@diary_app.command("demo")
def diary_demo(project_path: Path):
    """Create a demo timeline and write a production diary."""
    project_path.mkdir(parents=True, exist_ok=True)

    bus = EventBus()
    diary = ProductionDiary(project_path)
    diary.connect(bus)

    timeline = Timeline(event_bus=bus)

    beat = timeline.add(StoryBeatEvent(
        start=0.0,
        duration=4.0,
        goal="The boy looks toward the glowing village and considers leaving home.",
        emotion="hope",
        importance="high",
    ))

    clip = timeline.add(VideoClipEvent(
        start=0.0,
        duration=4.0,
        clip_path="assets/videos/shot_001.mp4",
        shot_id="shot_001",
    ))

    timeline.add(ReviewEvent(
        start=0.0,
        duration=4.0,
        score=92,
        comment="Strong establishing shot. Keep for director's cut.",
        target_event_id=clip.id,
    ))

    output = diary.write()
    print(f"[green]Production diary written:[/green] {output}")


if __name__ == "__main__":
    app()
