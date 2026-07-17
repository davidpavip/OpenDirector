from __future__ import annotations

import asyncio
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version
from pathlib import Path

import typer

from opendirector.applications import PlanningApplication
from opendirector.applications import (
    PlanningApplication,
    SketchApplication,
)

app = typer.Typer(
    name="opendirector",
    help="OpenDirector Creative Studio command-line interface.",
    no_args_is_help=True,
)


@app.command()
def plan(
    production: Path = typer.Argument(
        ...,
        help="Production directory containing source.md.",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
    ),
    approved_by: str = typer.Option(
        "Gilbert",
        "--approved-by",
        help="Name of the filmmaker approving the blueprint.",
    ),
) -> None:
    """Plan a production and create its blueprint."""

    source_path = production / "source.md"

    if not source_path.is_file():
        typer.secho(
            f"Source document not found: {source_path}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    typer.echo()
    typer.secho(
        "OpenDirector Studio",
        fg=typer.colors.CYAN,
        bold=True,
    )
    typer.echo(f"Production: {production.name}")
    typer.echo(f"Source:     {source_path}")
    typer.echo()

    application = PlanningApplication()

    try:
        blueprint_path = asyncio.run(
            application.run(
                production_dir=production,
                approved_by=approved_by,
            )
        )
    except Exception as exc:
        typer.secho(
            f"Planning failed: {exc}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1) from exc

    typer.secho(
        "Production planning completed.",
        fg=typer.colors.GREEN,
        bold=True,
    )
    typer.echo(f"Blueprint: {blueprint_path}")


@app.command()
def sketch(
    production: Path = typer.Argument(
        ...,
        help="Production directory.",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
    ),
    scene_id: str = typer.Argument(
        ...,
        help="Scene identifier, for example scene-001.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Regenerate sketches that already exist.",
    ),
) -> None:
    """Create visual sketches for one planned scene."""

    typer.echo()
    typer.secho(
        "OpenDirector Sketch",
        fg=typer.colors.CYAN,
        bold=True,
    )
    typer.echo(f"Production: {production.name}")
    typer.echo(f"Scene:      {scene_id}")
    typer.echo()

    application = SketchApplication()

    try:
        products = asyncio.run(
            application.run(
                production_dir=production,
                scene_id=scene_id,
                force=force,
            )
        )
    except Exception as exc:
        typer.secho(
            f"Sketch failed: {exc}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1) from exc

    typer.secho(
        "Scene sketch completed.",
        fg=typer.colors.GREEN,
        bold=True,
    )

    for product in products:
        typer.echo(f"Sketch: {product}")


@app.command()
def version() -> None:
    """Display the installed OpenDirector version."""

    try:
        value = package_version("opendirector")
    except PackageNotFoundError:
        value = "development"

    typer.echo(f"OpenDirector {value}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
