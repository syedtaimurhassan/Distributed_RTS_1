"""Batch orchestration for running the scaffold across multiple input CSV files."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from drts_mp1.orchestration.manifest import write_batch_manifest
from drts_mp1.orchestration.run_one import run_one


def run_batch(
    input_dir: str | Path,
    policies: Sequence[str] | None,
    stop_rule: str,
    out_root: str | Path,
    k: int = 1,
) -> list[dict[str, object]]:
    """Run all discovered task-set CSV files recursively and write manifest summary."""
    source_dir = Path(input_dir).resolve()
    out_dir = Path(out_root).resolve()

    discovered = sorted(
        path.resolve() for path in source_dir.rglob("*.csv") if path.is_file()
    )
    csv_files = [
        path
        for path in discovered
        if not path.is_relative_to(out_dir)
    ]

    entries: list[dict[str, object]] = []
    for csv_file in csv_files:
        try:
            run_info = run_one(
                taskset_csv_path=csv_file,
                policies=policies,
                stop_rule=stop_rule,
                out_root=out_root,
                k=k,
            )
            entries.append(
                {
                    "run_id": run_info.get("run_id", ""),
                    "input_file": str(csv_file),
                    "run_folder": run_info.get("run_dir", ""),
                    "status": "success",
                    "error": "",
                    "task_count": run_info.get("task_count"),
                    "utilization_total": run_info.get("utilization_total"),
                    "hyperperiod": run_info.get("hyperperiod"),
                    "policies": ",".join(run_info.get("policies", [])),
                    "stop_rule": run_info.get("stop_rule"),
                    "stop_time": run_info.get("stop_time"),
                    "dm_all_schedulable": run_info.get("dm_all_schedulable"),
                    "edf_feasible": run_info.get("edf_feasible"),
                    "sim_rm_deadline_misses": run_info.get("sim_rm_deadline_misses"),
                    "sim_dm_deadline_misses": run_info.get("sim_dm_deadline_misses"),
                    "sim_edf_deadline_misses": run_info.get("sim_edf_deadline_misses"),
                }
            )
        except Exception as exc:  # noqa: BLE001
            entries.append(
                {
                    "run_id": "",
                    "input_file": str(csv_file),
                    "run_folder": "",
                    "status": "error",
                    "error": str(exc),
                    "task_count": "",
                    "utilization_total": "",
                    "hyperperiod": "",
                    "policies": ",".join(policies or []),
                    "stop_rule": stop_rule,
                    "stop_time": "",
                    "dm_all_schedulable": "",
                    "edf_feasible": "",
                    "sim_rm_deadline_misses": "",
                    "sim_dm_deadline_misses": "",
                    "sim_edf_deadline_misses": "",
                }
            )

    write_batch_manifest(Path(out_root) / "batch_manifest.csv", entries)
    return entries
