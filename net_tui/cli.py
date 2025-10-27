import argparse

def build_parser():
    parser = argparse.ArgumentParser(
        prog="net-tui",
        description="net-tui: TUI/CLI для настроек сети (systemd-networkd)",
    )
    return parser

def main(argv=None) -> int:
    parser = build_parser()
    parser.parse_args(argv)
    return 0