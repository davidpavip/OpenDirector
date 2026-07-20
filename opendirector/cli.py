from __future__ import annotations

import asyncio
from pathlib import Path

import typer
from opendirector.applications import PlanningApplication

app = typer.Typer(
    name="opendirector",
    help="OpenDirector Creative Studio command-line interface.",
    no_args_is_help=True,
)


@app.command()
def plan(
    production: Path = typer.Argument(
        ...,
        help="Production workspace containing source.md.",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
    ),
    approved_by: str = typer.Option(
        "Gilbert",
        "--approved-by",
        help="Name recorded as blueprint approver.",
    ),
) -> None:
    """Plan a production and create planning.md and blueprint.md."""

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

    planning_path = production / "planning.md"

    if not blueprint_path.is_file():
        typer.secho(
            "Planning completed but blueprint.md was not created.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    if not planning_path.is_file():
        typer.secho(
            "Planning completed but planning.md was not created.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    typer.echo()
    typer.secho(
        "✓ Production planning completed",
        fg=typer.colors.GREEN,
        bold=True,
    )
    typer.echo(f"Planning:  {planning_path}")
    typer.echo(f"Blueprint: {blueprint_path}")


@app.command()
def version() -> None:
    """Display the installed OpenDirector version."""

    try:
        from importlib.metadata import version as package_version

        value = package_version("opendirector")
    except Exception:
        value = "development"

    typer.echo(f"OpenDirector {value}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
