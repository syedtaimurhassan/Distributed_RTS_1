"""Comparison helpers between analytical and simulation results."""

from __future__ import annotations

from drts_mp1.domain.results import AnalysisResult, CompareResult, SimResult


def compare_dm_rta_vs_sim_dm(
    analysis_result: AnalysisResult,
    sim_result: SimResult,
) -> CompareResult:
    """Compare DM RTA per-task bounds against DM simulation outputs."""
    sim_by_task = {row.task_id: row for row in sim_result.task_rows}
    rows: list[dict[str, object]] = []

    for dm_row in analysis_result.dm_rta_rows:
        sim_row = sim_by_task.get(dm_row.task_id)
        sim_worst = sim_row.worst_response_time if sim_row is not None else None
        difference: float | None = None
        if dm_row.rta_wcrt_ri is not None and sim_worst is not None:
            difference = float(dm_row.rta_wcrt_ri) - float(sim_worst)

        rows.append(
            {
                "TaskID": dm_row.task_id,
                "RTA_WCRT_Ri": dm_row.rta_wcrt_ri,
                "Sim_WorstResponseTime": sim_worst,
                "Difference": difference,
            }
        )

    return CompareResult(rows=rows)


def compare_edf_pdc_vs_sim_edf(
    analysis_result: AnalysisResult,
    sim_result: SimResult,
) -> CompareResult:
    """Compare EDF PDC feasibility against EDF simulation deadline misses."""
    feasible = (
        analysis_result.edf_pdc_summary.feasible
        if analysis_result.edf_pdc_summary is not None
        else None
    )
    misses_total = sim_result.deadline_misses_total
    agreement: bool | None = None

    if feasible is not None:
        agreement = bool((feasible and misses_total == 0) or (not feasible and misses_total > 0))

    return CompareResult(
        rows=[
            {
                "EDF_PDC_Feasible": feasible,
                "Sim_DeadlineMisses_Total": misses_total,
                "Agreement": agreement,
            }
        ]
    )
