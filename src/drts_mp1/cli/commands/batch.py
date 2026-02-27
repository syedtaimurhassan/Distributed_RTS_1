"""`batch` command: run scaffold for all CSV files in a directory."""

from __future__ import annotations

import argparse

from drts_mp1.orchestration.run_batch import run_batch


def _parse_policy_list(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def handle_batch(args: argparse.Namespace) -> int:
    run_batch(
        input_dir=args.dir,
        policies=_parse_policy_list(args.policies),
        stop_rule=args.stop,
        out_root=args.out,
        k=args.k,
    )
    return 0


def add_subparser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        "batch",
        help="Run analysis + simulation over all *.csv files recursively in a directory.",
    )
    parser.add_argument("dir", help="Directory containing task-set CSV files.")
    parser.add_argument(
        "--policies",
        default="rm,dm,edf",
        help="Comma-separated policy list (e.g. rm,dm,edf).",
    )
    parser.add_argument(
        "--stop",
        default="H",
        choices=["H", "kH"],
        help="Simulation stop rule (H or kH).",
    )
    parser.add_argument(
        "--k",
        type=int,
        default=1,
        help="Multiplier used when --stop kH (default: 1).",
    )
    parser.add_argument(
        "--out",
        default="results/runs",
        help="Output root for run folders (default: results/runs).",
    )
    parser.set_defaults(handler=handle_batch)
