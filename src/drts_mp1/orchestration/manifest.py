"""Batch manifest writer for linking input files to run IDs."""

from __future__ import annotations

import csv
from collections.abc import Iterable
from pathlib import Path

BATCH_MANIFEST_COLUMNS: tuple[str, ...] = (
    "run_group",
    "run_id",
    "input_file",
    "run_folder",
    "status",
    "error",
    "task_count",
    "utilization_total",
    "hyperperiod",
    "policies",
    "execution_mode",
    "core_count",
    "active_cores",
    "stop_rule",
    "stop_time",
    "sim_execution_time_mode",
    "sim_random_seed",
    "dm_all_schedulable",
    "edf_wcrt_all_schedulable",
    "edf_feasible",
    "sim_rm_deadline_misses",
    "sim_dm_deadline_misses",
    "sim_edf_deadline_misses",
)


def write_batch_manifest(manifest_path: str | Path, entries: Iterable[dict[str, object]]) -> Path:
    """Write a batch-level manifest CSV with one row per processed input file."""
    path = Path(manifest_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(BATCH_MANIFEST_COLUMNS))
        writer.writeheader()
        for entry in entries:
            writer.writerow({column: entry.get(column, "") for column in BATCH_MANIFEST_COLUMNS})
    return path
