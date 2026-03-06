"""Run-one orchestration: parse, validate, analyze, simulate, and write CSVs."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from drts_mp1.analysis.dm_rta import compute_dm_rta
from drts_mp1.analysis.edf_pdc import check_edf_pdc
from drts_mp1.analysis.edf_wcrt import compute_edf_wcrt
from drts_mp1.domain.results import AnalysisResult, CompareResult, EDFPDCSummary, SimResult
from drts_mp1.domain.taskset import TaskSet
from drts_mp1.io.output_csv import (
    COMPARE_DM_COLUMNS,
    COMPARE_EDF_COLUMNS,
    COMPARE_EDF_WCRT_COLUMNS,
    write_analysis_dm_rta_csv,
    write_analysis_edf_pdc_points_csv,
    write_analysis_edf_pdc_summary_csv,
    write_analysis_edf_wcrt_csv,
    write_compare_csv,
    write_run_log_txt,
    write_run_metadata_csv,
    write_sim_jobs_csv,
    write_sim_tasks_csv,
)
from drts_mp1.io.paths import (
    copy_input_taskset,
    create_run_folder,
    create_run_group_folder,
    create_run_id,
)
from drts_mp1.io.taskset_csv import read_taskset_csv
from drts_mp1.io.validation import validate_taskset
from drts_mp1.orchestration.compare import (
    compare_dm_rta_vs_sim_dm,
    compare_edf_pdc_vs_sim_edf,
    compare_edf_wcrt_vs_sim_edf,
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


def _enforce_single_core_pe(taskset: TaskSet) -> list[str]:
    """Ensure the input is consistent with a single-core execution model.

    The project uses one processor/core. `PE` is treated as input metadata only,
    but all tasks must refer to the same processing element for this mode.
    """
    pe_values = {task.pe for task in taskset.tasks if task.pe is not None}
    if len(pe_values) > 1:
        sorted_values = ", ".join(str(value) for value in sorted(pe_values))
        raise ValueError(
            "Single-core mode requires a single PE value across all tasks. "
            f"Found multiple PE values: {sorted_values}"
        )

    warnings: list[str] = []
    if pe_values:
        only_pe = next(iter(pe_values))
        warnings.append(
            f"Single-core mode active: using one core; PE column retained as metadata "
            f"(value={only_pe}) and ignored by scheduling."
        )
    else:
        warnings.append(
            "Single-core mode active: using one core; PE column is missing/empty in tasks."
        )
    return warnings


def _validate_execution_mode(execution_mode: str) -> str:
    mode = execution_mode.strip().lower()
    if mode not in {"single", "multi"}:
        raise ValueError("Unsupported execution mode. Use 'single' or 'multi'.")
    return mode


def _validate_execution_time_mode(execution_time_mode: str) -> str:
    mode = execution_time_mode.strip().lower()
    if mode not in {"wcet", "uniform"}:
        raise ValueError("Unsupported simulation execution-time mode. Use 'wcet' or 'uniform'.")
    return mode


def _partition_for_execution(
    taskset: TaskSet,
    execution_mode: str,
    core_count: int,
) -> tuple[dict[int, TaskSet], list[str]]:
    """Build per-core task sets according to selected execution mode."""
    if core_count <= 0:
        raise ValueError("--cores must be a positive integer.")

    mode = _validate_execution_mode(execution_mode)

    if mode == "single":
        warnings = _enforce_single_core_pe(taskset)
        return {0: TaskSet(tasks=list(taskset.tasks))}, warnings

    if not taskset.tasks:
        return {}, ["Multi-core mode active: empty task set."]

    raw_pe_values: list[int] = []
    for task in taskset.tasks:
        if task.pe is None:
            raise ValueError(
                "Multi-core mode requires PE for every task; found a task with empty PE."
            )
        raw_pe_values.append(task.pe)

    min_pe = min(raw_pe_values)
    max_pe = max(raw_pe_values)

    if 0 <= min_pe and max_pe < core_count:
        offset = 0
    elif 1 <= min_pe and max_pe <= core_count:
        offset = 1
    else:
        raise ValueError(
            "PE values do not match configured --cores. "
            f"Observed PE range [{min_pe}, {max_pe}] with cores={core_count}."
        )

    grouped: dict[int, list] = {}
    for task in taskset.tasks:
        assert task.pe is not None
        core_id = task.pe - offset
        grouped.setdefault(core_id, []).append(task)

    if any(core_id < 0 or core_id >= core_count for core_id in grouped):
        raise ValueError("Computed core mapping produced out-of-range core index.")

    core_tasksets = {
        core_id: TaskSet(tasks=tasks)
        for core_id, tasks in sorted(grouped.items(), key=lambda item: item[0])
    }
    warnings = [
        "Multi-core mode active: tasks partitioned by PE values "
        f"(cores={core_count}, pe_index_offset={offset}, active_cores={len(core_tasksets)}).",
    ]
    return core_tasksets, warnings


def _merge_sim_results(policy_name: str, stop_time: int, core_results: Sequence[SimResult]) -> SimResult:
    """Merge per-core simulation outputs into one policy-level result container."""
    merged_jobs = []
    merged_task_rows = []
    deadline_misses_total = 0
    for result in core_results:
        merged_jobs.extend(result.jobs)
        merged_task_rows.extend(result.task_rows)
        deadline_misses_total += result.deadline_misses_total
    return SimResult(
        policy=policy_name,
        stop_time=stop_time,
        jobs=merged_jobs,
        task_rows=merged_task_rows,
        deadline_misses_total=deadline_misses_total,
    )


def _run_analysis_for_mode(
    taskset: TaskSet,
    core_tasksets: dict[int, TaskSet],
    execution_mode: str,
    run_log_lines: list[str],
) -> tuple[AnalysisResult, AnalysisResult, AnalysisResult]:
    """Run analysis for selected mode.

    - single: one global analysis on full task set.
    - multi: per-core uniprocessor analysis; DM rows are concatenated and EDF
      feasibility is aggregated (all cores feasible).
    """
    mode = _validate_execution_mode(execution_mode)
    if mode == "single":
        return compute_dm_rta(taskset), check_edf_pdc(taskset), compute_edf_wcrt(taskset)

    dm_rows = []
    edf_wcrt_rows = []
    all_core_feasible = True
    for core_id, core_taskset in core_tasksets.items():
        dm_core = compute_dm_rta(core_taskset)
        edf_core = check_edf_pdc(core_taskset)
        edf_wcrt_core = compute_edf_wcrt(core_taskset)
        dm_rows.extend(dm_core.dm_rta_rows)
        edf_wcrt_rows.extend(edf_wcrt_core.edf_wcrt_rows)
        feasible = (
            edf_core.edf_pdc_summary.feasible
            if edf_core.edf_pdc_summary is not None
            else None
        )
        if feasible is False:
            all_core_feasible = False
        run_log_lines.append(
            f"analysis.core={core_id} task_count={len(core_taskset.tasks)} "
            f"utilization={core_taskset.utilization():.6f} edf_feasible={feasible}"
        )

    dm_analysis = AnalysisResult(dm_rta_rows=dm_rows)
    edf_wcrt_analysis = AnalysisResult(edf_wcrt_rows=edf_wcrt_rows)
    edf_summary = EDFPDCSummary(
        u_total=taskset.utilization(),
        h_hyperperiod=taskset.hyperperiod(),
        d_max=max((task.deadline for task in taskset.tasks), default=0),
        l_star=None,
        test_bound=None,
        feasible=all_core_feasible,
    )
    edf_analysis = AnalysisResult(edf_pdc_summary=edf_summary, edf_pdc_points=[])
    run_log_lines.append(
        "analysis.multi_core_note=EDF summary is aggregated across per-core "
        "uniprocessor checks; detailed per-core data is recorded in this log."
    )
    return dm_analysis, edf_analysis, edf_wcrt_analysis


def run_one(
    taskset_csv_path: str | Path,
    policies: Sequence[str] | None,
    stop_rule: str,
    out_root: str | Path,
    k: int = 1,
    execution_mode: str = "single",
    core_count: int = 1,
    sim_execution_time_mode: str = "wcet",
    sim_random_seed: int | None = None,
    run_group_dir: str | Path | None = None,
) -> dict[str, object]:
    """Execute one run and write all available CSV artifacts.

    This function wires input parsing, analyses, per-policy simulation, and output CSVs
    into one reproducible run folder.
    """
    taskset_path = Path(taskset_csv_path)
    taskset = read_taskset_csv(taskset_path)
    mode = _validate_execution_mode(execution_mode)
    sim_exec_mode = _validate_execution_time_mode(sim_execution_time_mode)
    warnings = validate_taskset(taskset)
    core_tasksets, mode_warnings = _partition_for_execution(
        taskset=taskset,
        execution_mode=mode,
        core_count=core_count,
    )
    warnings.extend(mode_warnings)

    if run_group_dir is None:
        group_dir = create_run_group_folder(
            out_root=out_root,
            execution_mode=mode,
            core_count=core_count,
        )
    else:
        group_dir = Path(run_group_dir)
        group_dir.mkdir(parents=True, exist_ok=True)

    run_id = create_run_id(taskset_path)
    run_dir = create_run_folder(out_root=group_dir, run_id=run_id)
    run_log_lines: list[str] = [
        f"run_group_dir={group_dir}",
        f"run_id={run_id}",
        f"taskset_path={taskset_path.resolve()}",
        f"execution_mode={mode}",
        f"core_count={core_count}",
        f"sim_execution_time_mode={sim_exec_mode}",
        f"sim_random_seed={sim_random_seed}",
    ]
    if core_tasksets:
        for core_id, core_taskset in core_tasksets.items():
            run_log_lines.append(
                f"core={core_id} task_count={len(core_taskset.tasks)} "
                f"utilization={core_taskset.utilization():.6f}"
            )

    copy_input_taskset(taskset_path=taskset_path, run_dir=run_dir)

    dm_analysis, edf_analysis, edf_wcrt_analysis = _run_analysis_for_mode(
        taskset=taskset,
        core_tasksets=core_tasksets,
        execution_mode=mode,
        run_log_lines=run_log_lines,
    )

    write_analysis_dm_rta_csv(run_dir, dm_analysis)
    write_analysis_edf_pdc_summary_csv(run_dir, edf_analysis)
    write_analysis_edf_pdc_points_csv(run_dir, edf_analysis)
    write_analysis_edf_wcrt_csv(run_dir, edf_wcrt_analysis)

    selected_policies = _normalize_policies(policies)
    hyperperiod = taskset.hyperperiod()
    stop_time = _resolve_stop_time(hyperperiod=hyperperiod, stop_rule=stop_rule, k=k)
    run_log_lines.append(f"stop_rule={stop_rule}")
    run_log_lines.append(f"stop_time={stop_time}")
    run_log_lines.append(f"policies={','.join(selected_policies)}")

    sim_results: dict[str, SimResult] = {}
    for name in selected_policies:
        core_results: list[SimResult] = []
        for core_id, core_taskset in sorted(core_tasksets.items(), key=lambda item: item[0]):
            policy = _POLICY_FACTORIES[name]()
            core_result = run_simulation(
                taskset=core_taskset,
                policy=policy,
                stop_time=stop_time,
                execution_time_mode=sim_exec_mode,
                random_seed=sim_random_seed,
                drain_after_stop=True,
            )
            core_results.append(core_result)
            run_log_lines.append(
                f"simulate.policy={name} core={core_id} jobs={len(core_result.jobs)} "
                f"deadline_misses={core_result.deadline_misses_total}"
            )

        sim_result = _merge_sim_results(
            policy_name=name,
            stop_time=stop_time,
            core_results=core_results,
        )
        sim_results[name] = sim_result
        write_sim_jobs_csv(run_dir=run_dir, policy=name, result=sim_result)
        write_sim_tasks_csv(run_dir=run_dir, policy=name, result=sim_result)

    if "dm" in sim_results:
        dm_compare = compare_dm_rta_vs_sim_dm(dm_analysis, sim_results["dm"])
    else:
        dm_compare = CompareResult(rows=[])

    if "edf" in sim_results:
        edf_compare = compare_edf_pdc_vs_sim_edf(edf_analysis, sim_results["edf"])
        edf_wcrt_compare = compare_edf_wcrt_vs_sim_edf(edf_wcrt_analysis, sim_results["edf"])
    else:
        edf_compare = CompareResult(rows=[])
        edf_wcrt_compare = CompareResult(rows=[])

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
    write_compare_csv(
        csv_path=run_dir / "compare_edf_wcrt_vs_sim_edf.csv",
        columns=COMPARE_EDF_WCRT_COLUMNS,
        result=edf_wcrt_compare,
    )

    metadata = {
        "run_group_dir": str(group_dir),
        "run_id": run_id,
        "taskset_path": str(taskset_path.resolve()),
        "policies": ",".join(selected_policies),
        "core_model": "single_core" if mode == "single" else "multi_core",
        "execution_mode": mode,
        "core_count": core_count,
        "active_cores": len(core_tasksets),
        "pe_handling": (
            "ignored_for_scheduling"
            if mode == "single"
            else "used_for_core_partitioning"
        ),
        "stop_rule": stop_rule,
        "stop_time": stop_time,
        "sim_execution_time_mode": sim_exec_mode,
        "sim_random_seed": sim_random_seed,
        "utilization_total": taskset.utilization(),
        "hyperperiod": hyperperiod,
        "warnings": " | ".join(warnings),
    }
    write_run_metadata_csv(run_dir=run_dir, metadata=metadata)
    write_run_log_txt(run_dir=run_dir, lines=run_log_lines + [f"warnings={' | '.join(warnings)}"])

    dm_all_schedulable = all(row.schedulable is True for row in dm_analysis.dm_rta_rows)
    edf_wcrt_all_schedulable = all(
        row.schedulable is True for row in edf_wcrt_analysis.edf_wcrt_rows
    )
    edf_feasible = (
        edf_analysis.edf_pdc_summary.feasible
        if edf_analysis.edf_pdc_summary is not None
        else None
    )

    return {
        "run_group_dir": str(group_dir),
        "run_id": run_id,
        "run_dir": str(run_dir),
        "taskset_path": str(taskset_path.resolve()),
        "policies": selected_policies,
        "execution_mode": mode,
        "core_count": core_count,
        "active_cores": len(core_tasksets),
        "stop_rule": stop_rule,
        "stop_time": stop_time,
        "sim_execution_time_mode": sim_exec_mode,
        "sim_random_seed": sim_random_seed,
        "task_count": len(taskset.tasks),
        "utilization_total": taskset.utilization(),
        "hyperperiod": hyperperiod,
        "dm_all_schedulable": dm_all_schedulable,
        "edf_wcrt_all_schedulable": edf_wcrt_all_schedulable,
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
