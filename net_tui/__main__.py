from .cli import run

if __name__ == "__main__":
    # Route -m net_tui to CLI, not TUI banner
    run(prog_name="net-tui")