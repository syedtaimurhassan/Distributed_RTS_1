"""`analyze` command: run analysis scaffolding and write CSV artifacts."""

from __future__ import annotations

import argparse

from drts_mp1.orchestration.run_one import run_one


def handle_analyze(args: argparse.Namespace) -> int:
    run_one(
        taskset_csv_path=args.taskset_csv,
        policies=[],
        stop_rule="H",
        out_root=args.out,
        k=1,
        execution_mode=args.execution_mode,
        core_count=args.cores,
    )
    return 0


def add_subparser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        "analyze",
        help="Run DM/EDF analysis scaffolding for one task-set CSV.",
    )
    parser.add_argument("taskset_csv", help="Path to task-set CSV file.")
    parser.add_argument(
        "--out",
        default="results/runs",
        help="Output root for run folders (default: results/runs).",
    )
    parser.add_argument(
        "--execution-mode",
        default="single",
        choices=["single", "multi"],
        help="Execution mode for PE handling during analysis (default: single).",
    )
    parser.add_argument(
        "--cores",
        type=int,
        default=1,
        help="Configured core count (default: 1).",
    )
    parser.set_defaults(handler=handle_analyze)
