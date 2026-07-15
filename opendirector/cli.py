from __future__ import annotations

import asyncio
from pathlib import Path

import typer

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
) -> None:
    """Plan a production and create an evolved blueprint."""

    source_path = production / "source.md"

    if not source_path.exists():
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

    # Production 001 compatibility bridge.
    #
    # The existing deterministic demonstration is currently specialized
    # for Little Robot. The next planning milestone will replace this
    # dispatch with a generic planning application.
    if production.name != "little_robot":
        typer.secho(
            "The current deterministic planner supports " "'little_robot' only.",
            fg=typer.colors.YELLOW,
        )
        typer.echo(
            "Generic source-to-blueprint planning will be introduced "
            "in the next milestone."
        )
        raise typer.Exit(code=2)

    from examples.run_little_robot_production import main as run_planning

    try:
        asyncio.run(run_planning())
    except Exception as exc:
        typer.secho(
            f"Planning failed: {exc}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1) from exc

    blueprint_path = production / "blueprint.md"

    if not blueprint_path.exists():
        typer.secho(
            "Planning completed but blueprint.md was not created.",
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
