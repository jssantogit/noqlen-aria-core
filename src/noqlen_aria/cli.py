"""Thin local development CLI for Noqlen Aria Core."""

from __future__ import annotations

import argparse
import platform
import sys

from noqlen_aria import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="noqlen-aria",
        description="Noqlen Aria Core development adapter.",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser(
        "doctor",
        help="Print safe local package/status information.",
    )
    return parser


def run_doctor() -> int:
    print("Noqlen Aria Core doctor")
    print(f"version: {__version__}")
    print(f"python: {platform.python_version()}")
    print(f"platform: {platform.system().lower() or 'unknown'}")
    print("anchor: not configured in Bloco 0")
    print("navidrome: not accessed")
    print("music-library: not accessed")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "doctor":
        return run_doctor()

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
