"""`simulate` command: run one policy simulation scaffold and write CSV artifacts."""

from __future__ import annotations

import argparse

from drts_mp1.orchestration.run_one import run_one


def handle_simulate(args: argparse.Namespace) -> int:
    run_one(
        taskset_csv_path=args.taskset_csv,
        policies=[args.policy],
        stop_rule=args.stop,
        out_root=args.out,
        k=args.k,
    )
    return 0


def add_subparser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        "simulate",
        help="Run simulation scaffold for one policy and one task-set CSV.",
    )
    parser.add_argument("taskset_csv", help="Path to task-set CSV file.")
    parser.add_argument(
        "--policy",
        required=True,
        choices=["rm", "dm", "edf"],
        help="Scheduling policy to simulate.",
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
    parser.set_defaults(handler=handle_simulate)
