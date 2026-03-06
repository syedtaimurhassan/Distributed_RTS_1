"""`run` command: run full scaffold for selected policies on one CSV."""

from __future__ import annotations

import argparse

from drts_mp1.orchestration.run_one import run_one


def _parse_policy_list(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def handle_run(args: argparse.Namespace) -> int:
    run_one(
        taskset_csv_path=args.taskset_csv,
        policies=_parse_policy_list(args.policies),
        stop_rule=args.stop,
        out_root=args.out,
        k=args.k,
        execution_mode=args.execution_mode,
        core_count=args.cores,
        sim_execution_time_mode=args.exec_time,
        sim_random_seed=args.seed,
    )
    return 0


def add_subparser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        "run",
        help="Run analysis + selected policy simulations for one task-set CSV.",
    )
    parser.add_argument("taskset_csv", help="Path to task-set CSV file.")
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
    parser.add_argument(
        "--execution-mode",
        default="single",
        choices=["single", "multi"],
        help="Execution mode: single-core or PE-partitioned multi-core (default: single).",
    )
    parser.add_argument(
        "--cores",
        type=int,
        default=1,
        help="Configured core count (default: 1). In multi mode, PE must map into this range.",
    )
    parser.add_argument(
        "--exec-time",
        default="wcet",
        choices=["wcet", "uniform"],
        help="Execution-time model: fixed WCET or uniform integer in [BCET, WCET] (default: wcet).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional RNG seed used when --exec-time uniform.",
    )
    parser.set_defaults(handler=handle_run)
