"""CSV writers for all required Mini-project 1 outputs."""

from __future__ import annotations

import csv
from fractions import Fraction
from pathlib import Path
from typing import Mapping, Sequence

from drts_mp1.domain.results import AnalysisResult, CompareResult, SimResult

RUN_METADATA_COLUMNS: tuple[str, str] = ("key", "value")

ANALYSIS_DM_RTA_COLUMNS: tuple[str, ...] = (
    "TaskID",
    "WCET_C",
    "Period_T",
    "Deadline_D",
    "PriorityOrder",
    "RTA_WCRT_Ri",
    "Schedulable",
    "Iterations",
)

ANALYSIS_EDF_PDC_SUMMARY_COLUMNS: tuple[str, ...] = (
    "U_total",
    "H_hyperperiod",
    "D_max",
    "L_star",
    "TestBound",
    "Feasible",
)

ANALYSIS_EDF_PDC_POINTS_COLUMNS: tuple[str, ...] = ("t", "dbf_t", "Pass")

SIM_JOBS_COLUMNS: tuple[str, ...] = (
    "TaskID",
    "JobIndex",
    "ReleaseTime",
    "AbsDeadline",
    "StartTime",
    "FinishTime",
    "ResponseTime",
    "MetDeadline",
    "Preemptions",
)

SIM_TASKS_COLUMNS: tuple[str, ...] = (
    "TaskID",
    "WCET_C",
    "Period_T",
    "Deadline_D",
    "JobsSimulated",
    "WorstResponseTime",
    "AvgResponseTime",
    "MinResponseTime",
    "DeadlineMisses",
    "PreemptionsTotal",
    "RRJ",
    "ARJ",
)

COMPARE_DM_COLUMNS: tuple[str, ...] = (
    "TaskID",
    "RTA_WCRT_Ri",
    "Sim_WorstResponseTime",
    "Difference",
)

COMPARE_EDF_COLUMNS: tuple[str, ...] = (
    "EDF_PDC_Feasible",
    "Sim_DeadlineMisses_Total",
    "Agreement",
)


def _to_cell(value: object) -> object:
    if value is None:
        return ""
    if isinstance(value, Fraction):
        if value.denominator == 1:
            return str(value.numerator)
        return f"{value.numerator}/{value.denominator}"
    return value


def _write_rows(path: Path, columns: Sequence[str], rows: Sequence[Mapping[str, object]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns))
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _to_cell(row.get(key)) for key in columns})
    return path


def write_run_metadata_csv(run_dir: str | Path, metadata: Mapping[str, object]) -> Path:
    """Write `run_metadata.csv` with (key,value) rows."""
    path = Path(run_dir) / "run_metadata.csv"
    rows = [{"key": key, "value": _to_cell(value)} for key, value in metadata.items()]
    return _write_rows(path, RUN_METADATA_COLUMNS, rows)


def write_analysis_dm_rta_csv(run_dir: str | Path, result: AnalysisResult) -> Path:
    """Write DM RTA per-task analysis CSV."""
    path = Path(run_dir) / "analysis_dm_rta.csv"
    rows = [
        {
            "TaskID": row.task_id,
            "WCET_C": row.wcet_c,
            "Period_T": row.period_t,
            "Deadline_D": row.deadline_d,
            "PriorityOrder": row.priority_order,
            "RTA_WCRT_Ri": row.rta_wcrt_ri,
            "Schedulable": row.schedulable,
            "Iterations": row.iterations,
        }
        for row in result.dm_rta_rows
    ]
    return _write_rows(path, ANALYSIS_DM_RTA_COLUMNS, rows)


def write_analysis_edf_pdc_summary_csv(run_dir: str | Path, result: AnalysisResult) -> Path:
    """Write EDF PDC summary CSV (single row expected)."""
    path = Path(run_dir) / "analysis_edf_pdc_summary.csv"
    rows: list[dict[str, object]] = []
    if result.edf_pdc_summary is not None:
        summary = result.edf_pdc_summary
        rows.append(
            {
                "U_total": summary.u_total,
                "H_hyperperiod": summary.h_hyperperiod,
                "D_max": summary.d_max,
                "L_star": summary.l_star,
                "TestBound": summary.test_bound,
                "Feasible": summary.feasible,
            }
        )
    return _write_rows(path, ANALYSIS_EDF_PDC_SUMMARY_COLUMNS, rows)


def write_analysis_edf_pdc_points_csv(run_dir: str | Path, result: AnalysisResult) -> Path:
    """Write EDF PDC test-point CSV."""
    path = Path(run_dir) / "analysis_edf_pdc_points.csv"
    rows = [
        {
            "t": point.t,
            "dbf_t": point.dbf_t,
            "Pass": point.passed,
        }
        for point in result.edf_pdc_points
    ]
    return _write_rows(path, ANALYSIS_EDF_PDC_POINTS_COLUMNS, rows)


def write_sim_jobs_csv(run_dir: str | Path, policy: str, result: SimResult) -> Path:
    """Write per-job simulation CSV for one policy."""
    path = Path(run_dir) / f"sim_jobs_{policy}.csv"
    rows = [
        {
            "TaskID": row.task_id,
            "JobIndex": row.job_index,
            "ReleaseTime": row.release_time,
            "AbsDeadline": row.abs_deadline,
            "StartTime": row.start_time,
            "FinishTime": row.finish_time,
            "ResponseTime": row.response_time,
            "MetDeadline": row.met_deadline,
            "Preemptions": row.preemptions,
        }
        for row in result.jobs
    ]
    return _write_rows(path, SIM_JOBS_COLUMNS, rows)


def write_sim_tasks_csv(run_dir: str | Path, policy: str, result: SimResult) -> Path:
    """Write per-task simulation summary CSV for one policy."""
    path = Path(run_dir) / f"sim_tasks_{policy}.csv"
    rows = [
        {
            "TaskID": row.task_id,
            "WCET_C": row.wcet_c,
            "Period_T": row.period_t,
            "Deadline_D": row.deadline_d,
            "JobsSimulated": row.jobs_simulated,
            "WorstResponseTime": row.worst_response_time,
            "AvgResponseTime": row.avg_response_time,
            "MinResponseTime": row.min_response_time,
            "DeadlineMisses": row.deadline_misses,
            "PreemptionsTotal": row.preemptions_total,
            "RRJ": row.rrj,
            "ARJ": row.arj,
        }
        for row in sorted(result.task_rows, key=lambda item: item.task_id)
    ]
    return _write_rows(path, SIM_TASKS_COLUMNS, rows)


def write_compare_csv(
    csv_path: str | Path,
    columns: Sequence[str],
    result: CompareResult,
) -> Path:
    """Write generic compare CSV from `CompareResult.rows`."""
    allowed = set(columns)
    rows = [{key: value for key, value in row.items() if key in allowed} for row in result.rows]
    if "TaskID" in allowed:
        rows.sort(key=lambda row: str(row.get("TaskID", "")))
    return _write_rows(Path(csv_path), columns, rows)
