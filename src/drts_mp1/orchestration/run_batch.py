"""Batch orchestration for running the scaffold across multiple input CSV files."""

from __future__ import annotations

import shutil
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path

from drts_mp1.io.paths import create_run_group_folder
from drts_mp1.orchestration.manifest import write_batch_manifest
from drts_mp1.orchestration.run_one import run_one


def run_batch(
    input_dir: str | Path,
    policies: Sequence[str] | None,
    stop_rule: str,
    out_root: str | Path,
    k: int = 1,
    execution_mode: str = "single",
    core_count: int = 1,
    sim_execution_time_mode: str = "wcet",
    sim_random_seed: int | None = None,
) -> list[dict[str, object]]:
    """Run all discovered task-set CSV files recursively and write manifest summary."""
    source_dir = Path(input_dir).resolve()
    out_dir = Path(out_root).resolve()
    group_dir = create_run_group_folder(
        out_root=out_root,
        execution_mode=execution_mode,
        core_count=core_count,
    )

    discovered = sorted(
        path.resolve() for path in source_dir.rglob("*.csv") if path.is_file()
    )
    csv_files = [
        path
        for path in discovered
        if not path.is_relative_to(out_dir)
    ]

    batch_log_path = group_dir / "batch_log.txt"
    batch_log_path.parent.mkdir(parents=True, exist_ok=True)
    batch_log_path.write_text(
        "\n".join(
            [
                f"batch_started_utc={datetime.now(timezone.utc).isoformat()}",
                f"input_dir={source_dir}",
                f"out_dir={out_dir}",
                f"run_group_dir={group_dir}",
                f"execution_mode={execution_mode}",
                f"core_count={core_count}",
                f"sim_execution_time_mode={sim_execution_time_mode}",
                f"sim_random_seed={sim_random_seed}",
                f"stop_rule={stop_rule}",
                f"k={k}",
                f"discovered_csv_files={len(csv_files)}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    entries: list[dict[str, object]] = []
    for csv_file in csv_files:
        try:
            run_info = run_one(
                taskset_csv_path=csv_file,
                policies=policies,
                stop_rule=stop_rule,
                out_root=out_root,
                k=k,
                execution_mode=execution_mode,
                core_count=core_count,
                sim_execution_time_mode=sim_execution_time_mode,
                sim_random_seed=sim_random_seed,
                run_group_dir=group_dir,
            )
            entries.append(
                {
                    "run_group": run_info.get("run_group_dir", ""),
                    "run_id": run_info.get("run_id", ""),
                    "input_file": str(csv_file),
                    "run_folder": run_info.get("run_dir", ""),
                    "status": "success",
                    "error": "",
                    "task_count": run_info.get("task_count"),
                    "utilization_total": run_info.get("utilization_total"),
                    "hyperperiod": run_info.get("hyperperiod"),
                    "policies": ",".join(run_info.get("policies", [])),
                    "execution_mode": run_info.get("execution_mode"),
                    "core_count": run_info.get("core_count"),
                    "active_cores": run_info.get("active_cores"),
                    "stop_rule": run_info.get("stop_rule"),
                    "stop_time": run_info.get("stop_time"),
                    "sim_execution_time_mode": run_info.get("sim_execution_time_mode"),
                    "sim_random_seed": run_info.get("sim_random_seed"),
                    "dm_all_schedulable": run_info.get("dm_all_schedulable"),
                    "edf_wcrt_all_schedulable": run_info.get("edf_wcrt_all_schedulable"),
                    "edf_feasible": run_info.get("edf_feasible"),
                    "sim_rm_deadline_misses": run_info.get("sim_rm_deadline_misses"),
                    "sim_dm_deadline_misses": run_info.get("sim_dm_deadline_misses"),
                    "sim_edf_deadline_misses": run_info.get("sim_edf_deadline_misses"),
                }
            )
        except Exception as exc:  # noqa: BLE001
            entries.append(
                {
                    "run_group": str(group_dir),
                    "run_id": "",
                    "input_file": str(csv_file),
                    "run_folder": "",
                    "status": "error",
                    "error": str(exc),
                    "task_count": "",
                    "utilization_total": "",
                    "hyperperiod": "",
                    "policies": ",".join(policies or []),
                    "execution_mode": execution_mode,
                    "core_count": core_count,
                    "active_cores": "",
                    "stop_rule": stop_rule,
                    "stop_time": "",
                    "sim_execution_time_mode": sim_execution_time_mode,
                    "sim_random_seed": sim_random_seed,
                    "dm_all_schedulable": "",
                    "edf_wcrt_all_schedulable": "",
                    "edf_feasible": "",
                    "sim_rm_deadline_misses": "",
                    "sim_dm_deadline_misses": "",
                    "sim_edf_deadline_misses": "",
                }
            )
        with batch_log_path.open("a", encoding="utf-8") as handle:
            latest = entries[-1]
            handle.write(
                "file="
                f"{latest.get('input_file')} "
                f"status={latest.get('status')} "
                f"run_id={latest.get('run_id')} "
                f"error={latest.get('error')}\n"
            )

    manifest_path = write_batch_manifest(group_dir / "batch_manifest.csv", entries)
    # Keep convenience copies at out_root pointing to the latest batch run.
    shutil.copyfile(manifest_path, out_dir / "batch_manifest.csv")
    shutil.copyfile(batch_log_path, out_dir / "batch_log.txt")
    with batch_log_path.open("a", encoding="utf-8") as handle:
        success_count = sum(1 for entry in entries if entry.get("status") == "success")
        error_count = sum(1 for entry in entries if entry.get("status") == "error")
        handle.write(f"success={success_count} error={error_count}\n")
    shutil.copyfile(batch_log_path, out_dir / "batch_log.txt")
    return entries
