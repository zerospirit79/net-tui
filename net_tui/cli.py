from __future__ import annotations
import typer
from typing import Optional

app = typer.Typer(help="TUI/CLI for network settings on ALT Linux")

@app.callback()
def main(
    verbose: int = typer.Option(0, "--verbose", "-v", count=True, help="Increase verbosity (-v, -vv)"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Assume Yes to prompts"),
):
    # TODO: setup logging by verbosity if needed
    pass

@app.command(help="Show current network status")
def status():
    # TODO: integrate with your core module
    print("Network status: (not implemented yet)")

@app.command(help="Apply configuration from file with safe backup")
def apply(
    config: str = typer.Argument(..., help="Path to configuration file (YAML/TOML)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not change system, just show plan"),
    backup_dir: Optional[str] = typer.Option(None, "--backup-dir", help="Backup directory"),
):
    # TODO: core.apply(config, dry_run, backup_dir)
    print(f"Applying configuration from {config} (dry_run={dry_run}, backup_dir={backup_dir})")

@app.command(help="Rollback last applied configuration")
def rollback(
    backup: Optional[str] = typer.Option(None, "--backup", help="Path to backup to restore"),
):
    # TODO: core.rollback(backup)
    print(f"Rolling back (backup={backup})")

@app.command(help="Interact with NetworkManager")
def nm(
    action: str = typer.Argument(..., help="Action: on|off|reload|status"),
):
    # TODO: core.nm(action)
    print(f"NetworkManager action: {action}")

@app.command(help="Interact with systemd-networkd")
def systemd(
    action: str = typer.Argument(..., help="Action: on|off|reload|status"),
):
    # TODO: core.systemd_networkd(action)
    print(f"systemd-networkd action: {action}")

@app.command(help="DNS via systemd-resolved")
def dns(
    action: str = typer.Argument(..., help="Action: show|flush|set"),
    value: Optional[str] = typer.Option(None, "--value", help="Value for set"),
):
    # TODO: core.resolved(action, value)
    print(f"systemd-resolved: {action}, value={value}")

@app.command(help="Launch TUI")
def tui():
    # TODO: import and run your Textual app when ready
    print("Launching TUI (not implemented yet)")

def run():
    app()

if __name__ == "__main__":
    run()