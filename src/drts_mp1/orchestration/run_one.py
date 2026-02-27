"""Run-one orchestration: parse, validate, analyze, simulate, and write CSVs."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from drts_mp1.analysis.dm_rta import compute_dm_rta
from drts_mp1.analysis.edf_pdc import check_edf_pdc
from drts_mp1.domain.results import CompareResult, SimResult
from drts_mp1.io.output_csv import (
    COMPARE_DM_COLUMNS,
    COMPARE_EDF_COLUMNS,
    write_analysis_dm_rta_csv,
    write_analysis_edf_pdc_points_csv,
    write_analysis_edf_pdc_summary_csv,
    write_compare_csv,
    write_run_metadata_csv,
    write_sim_jobs_csv,
    write_sim_tasks_csv,
)
from drts_mp1.io.paths import copy_input_taskset, create_run_folder, create_run_id
from drts_mp1.io.taskset_csv import read_taskset_csv
from drts_mp1.io.validation import validate_taskset
from drts_mp1.orchestration.compare import (
    compare_dm_rta_vs_sim_dm,
    compare_edf_pdc_vs_sim_edf,
)
from drts_mp1.simulation.engine import run_simulation
from drts_mp1.simulation.policies.dm import DMPolicy
from drts_mp1.simulation.policies.edf import EDFPolicy
from drts_mp1.simulation.policies.rm import RMPolicy

_POLICY_FACTORIES = {
    "rm": RMPolicy,
    "dm": DMPolicy,
    "edf": EDFPolicy,
}


def _normalize_policies(policies: Sequence[str] | None) -> list[str]:
    if policies is None:
        return ["rm", "dm", "edf"]
    if not policies:
        return []

    normalized: list[str] = []
    for policy in policies:
        name = policy.strip().lower()
        if not name:
            continue
        if name not in _POLICY_FACTORIES:
            raise ValueError(f"Unsupported policy '{policy}'. Choose from rm, dm, edf.")
        if name not in normalized:
            normalized.append(name)
    return normalized


def _resolve_stop_time(hyperperiod: int, stop_rule: str, k: int) -> int:
    if stop_rule == "H":
        return hyperperiod
    if stop_rule == "kH":
        if k <= 0:
            raise ValueError("--k must be a positive integer when --stop kH is used.")
        return hyperperiod * k
    raise ValueError("Unsupported stop rule. Use 'H' or 'kH'.")


def run_one(
    taskset_csv_path: str | Path,
    policies: Sequence[str] | None,
    stop_rule: str,
    out_root: str | Path,
    k: int = 1,
) -> dict[str, object]:
    """Execute one run and write all available CSV artifacts.

    This function wires input parsing, analyses, per-policy simulation, and output CSVs
    into one reproducible run folder.
    """
    taskset_path = Path(taskset_csv_path)
    taskset = read_taskset_csv(taskset_path)
    warnings = validate_taskset(taskset)

    run_id = create_run_id(taskset_path)
    run_dir = create_run_folder(out_root=out_root, run_id=run_id)

    copy_input_taskset(taskset_path=taskset_path, run_dir=run_dir)

    dm_analysis = compute_dm_rta(taskset)
    edf_analysis = check_edf_pdc(taskset)

    write_analysis_dm_rta_csv(run_dir, dm_analysis)
    write_analysis_edf_pdc_summary_csv(run_dir, edf_analysis)
    write_analysis_edf_pdc_points_csv(run_dir, edf_analysis)

    selected_policies = _normalize_policies(policies)
    hyperperiod = taskset.hyperperiod()
    stop_time = _resolve_stop_time(hyperperiod=hyperperiod, stop_rule=stop_rule, k=k)

    sim_results: dict[str, SimResult] = {}
    for name in selected_policies:
        policy = _POLICY_FACTORIES[name]()
        sim_result = run_simulation(taskset=taskset, policy=policy, stop_time=stop_time)
        sim_results[name] = sim_result
        write_sim_jobs_csv(run_dir=run_dir, policy=name, result=sim_result)
        write_sim_tasks_csv(run_dir=run_dir, policy=name, result=sim_result)

    if "dm" in sim_results:
        dm_compare = compare_dm_rta_vs_sim_dm(dm_analysis, sim_results["dm"])
    else:
        dm_compare = CompareResult(rows=[])

    if "edf" in sim_results:
        edf_compare = compare_edf_pdc_vs_sim_edf(edf_analysis, sim_results["edf"])
    else:
        edf_compare = CompareResult(rows=[])

    write_compare_csv(
        csv_path=run_dir / "compare_dm_rta_vs_sim_dm.csv",
        columns=COMPARE_DM_COLUMNS,
        result=dm_compare,
    )
    write_compare_csv(
        csv_path=run_dir / "compare_edf_pdc_vs_sim_edf.csv",
        columns=COMPARE_EDF_COLUMNS,
        result=edf_compare,
    )

    metadata = {
        "run_id": run_id,
        "taskset_path": str(taskset_path.resolve()),
        "policies": ",".join(selected_policies),
        "stop_rule": stop_rule,
        "stop_time": stop_time,
        "utilization_total": taskset.utilization(),
        "hyperperiod": hyperperiod,
        "warnings": " | ".join(warnings),
    }
    write_run_metadata_csv(run_dir=run_dir, metadata=metadata)

    dm_all_schedulable = all(row.schedulable is True for row in dm_analysis.dm_rta_rows)
    edf_feasible = (
        edf_analysis.edf_pdc_summary.feasible
        if edf_analysis.edf_pdc_summary is not None
        else None
    )

    return {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "taskset_path": str(taskset_path.resolve()),
        "policies": selected_policies,
        "stop_rule": stop_rule,
        "stop_time": stop_time,
        "task_count": len(taskset.tasks),
        "utilization_total": taskset.utilization(),
        "hyperperiod": hyperperiod,
        "dm_all_schedulable": dm_all_schedulable,
        "edf_feasible": edf_feasible,
        "sim_rm_deadline_misses": (
            sim_results["rm"].deadline_misses_total if "rm" in sim_results else None
        ),
        "sim_dm_deadline_misses": (
            sim_results["dm"].deadline_misses_total if "dm" in sim_results else None
        ),
        "sim_edf_deadline_misses": (
            sim_results["edf"].deadline_misses_total if "edf" in sim_results else None
        ),
    }
