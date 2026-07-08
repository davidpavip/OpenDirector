from __future__ import annotations

import argparse

from .core.project import Project
from .core.timeline import Timeline, timeline_from_shots
from .editor.exporter import export_simple_concat
from .plugins.renderers.ltx_api import LTXAPIRenderer


def inspect_project(args):
    project = Project(args.project)
    movie = project.load_movie()
    print(f"Project: {project.config.get('name', 'Untitled')}")
    print(f"Movie: {movie.title}")
    print(f"Scenes: {len(movie.scenes)}")
    print(f"Shots: {len(movie.shots)}")
    for scene in movie.scenes:
        print(f"  {scene.id}: {scene.title} ({len(scene.shots)} shots)")


def render_project(args):
    project = Project(args.project)
    movie = project.load_movie()
    renderer = LTXAPIRenderer(
        model=args.model or project.config.get("renderer", {}).get("model", "ltx-2-3-fast"),
        resolution=args.resolution or project.config.get("renderer", {}).get("resolution", "1920x1080"),
    )
    for shot in movie.shots:
        renderer.render_shot(project, shot, overwrite=args.overwrite)


def build_timeline(args):
    project = Project(args.project)
    movie = project.load_movie()
    fps = int(args.fps or project.config.get("fps", 24))
    timeline = timeline_from_shots(movie.shots, fps=fps, crossfade=float(args.crossfade))
    out = project.path(args.output)
    timeline.save(out)
    print(f"Timeline: {out}")
    print(f"Events: {len(timeline.events)}")
    print(f"Duration: {timeline.duration:.2f}s")


def inspect_timeline(args):
    timeline = Timeline.load(args.timeline)
    print(f"Timeline: {timeline.id}")
    print(f"FPS: {timeline.fps}")
    print(f"Duration: {timeline.duration:.2f}s")
    print(f"Events: {len(timeline.events)}")
    for event in timeline.events:
        asset = f" asset={event.asset}" if event.asset else ""
        print(f"  {event.start:7.2f}-{event.end:7.2f}  {event.track:12s} {event.kind:14s} {event.id}{asset}")


def export_timeline(args):
    project = Project(args.project)
    timeline = Timeline.load(project.path(args.timeline))
    out = export_simple_concat(project, timeline, args.output)
    print(f"Exported: {out}")


def main():
    parser = argparse.ArgumentParser(prog="opendirector")
    sub = parser.add_subparsers(required=True)

    p = sub.add_parser("inspect")
    p.add_argument("project")
    p.set_defaults(func=inspect_project)

    p = sub.add_parser("render")
    p.add_argument("project")
    p.add_argument("--model")
    p.add_argument("--resolution")
    p.add_argument("--overwrite", action="store_true")
    p.set_defaults(func=render_project)

    p = sub.add_parser("timeline")
    timeline_sub = p.add_subparsers(required=True)

    p_build = timeline_sub.add_parser("build")
    p_build.add_argument("project")
    p_build.add_argument("--output", default="edl/timeline_v1.json")
    p_build.add_argument("--fps", type=int)
    p_build.add_argument("--crossfade", type=float, default=0.0)
    p_build.set_defaults(func=build_timeline)

    p_inspect = timeline_sub.add_parser("inspect")
    p_inspect.add_argument("timeline")
    p_inspect.set_defaults(func=inspect_timeline)

    p_export = timeline_sub.add_parser("export")
    p_export.add_argument("project")
    p_export.add_argument("--timeline", default="edl/timeline_v1.json")
    p_export.add_argument("--output", default="export/director_cut_v1.mp4")
    p_export.set_defaults(func=export_timeline)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
