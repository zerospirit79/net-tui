import os
import sys
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
        None,
        "--color/--no-color",
        help="Enable or disable colored output.",
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
    from .tui import NetTuiApp
    NetTuiApp().run()

def run():
    app()