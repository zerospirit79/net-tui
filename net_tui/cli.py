import os
from typing import Optional
import typer

def should_color(force_color: Optional[bool]) -> bool:
    if force_color is True:
        return True
    if force_color is False:
        return False
    if os.environ.get("CLICOLOR_FORCE", "") not in ("", "0"):
        return True
    if os.environ.get("NO_COLOR"):
        return False
    return True

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help="net-tui — TUI/CLI utility for network configuration.",
)

@app.callback()
def _root(
    color: Optional[bool] = typer.Option(
        None, "--color/--no-color", help="Enable or disable colored output."
    )
):
    use_color = should_color(color)
    if use_color:
        os.environ.pop("NO_COLOR", None)
        os.environ["CLICOLOR"] = "1"
    else:
        os.environ["NO_COLOR"] = "1"
        os.environ["CLICOLOR"] = "0"

@app.command(help="Show version")
def version():
    import importlib.metadata as m
    typer.echo(m.version("net-tui"))

@app.command(help="Launch TUI interface")
def tui():
    try:
        from .tui import run_tui
    except Exception as e:
        typer.secho(
            "Failed to import TUI (net_tui.tui.run_tui). "
            "Ensure Textual is installed and net_tui/tui/app.py defines run_tui().\n"
            f"Original error: {e}",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=2)
    run_tui()

def run(prog_name: str | None = None):
    app(prog_name=prog_name or "net-tui")