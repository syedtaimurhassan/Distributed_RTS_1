"""CLI entrypoint for the Mini-project 1 scaffold."""

from __future__ import annotations

import argparse
import sys

from drts_mp1.cli.commands.analyze import add_subparser as add_analyze
from drts_mp1.cli.commands.batch import add_subparser as add_batch
from drts_mp1.cli.commands.run import add_subparser as add_run
from drts_mp1.cli.commands.simulate import add_subparser as add_simulate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="drts-mp1",
        description="Mini-project 1 scaffold CLI (analysis + simulation wiring).",
    )
    subparsers = parser.add_subparsers(dest="command")

    add_analyze(subparsers)
    add_simulate(subparsers)
    add_run(subparsers)
    add_batch(subparsers)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "handler"):
        parser.print_help()
        return 1

    try:
        return int(args.handler(args))
    except ValueError as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
