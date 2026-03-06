"""Result dataclasses used by analysis/simulation/orchestration CSV writers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DMRTARow:
    """Per-task DM RTA row."""

    task_id: str
    wcet_c: int
    period_t: int
    deadline_d: int
    priority_order: int | None = None
    rta_wcrt_ri: int | None = None
    schedulable: bool | None = None
    iterations: int | None = None


@dataclass
class EDFPDCSummary:
    """Single-row EDF PDC summary output."""

    u_total: str | float
    h_hyperperiod: int
    d_max: int
    l_star: str | int | None = None
    test_bound: int | None = None
    feasible: bool | None = None


@dataclass
class EDFPDCPoint:
    """Test point row for EDF dbf/PDC feasibility checking."""

    t: int
    dbf_t: int | None = None
    passed: bool | None = None


@dataclass
class EDFWCRTRow:
    """Per-task exact EDF WCRT row (synchronous periodic WCET model)."""

    task_id: str
    wcet_c: int
    period_t: int
    deadline_d: int
    jobs_in_hyperperiod: int
    edf_wcrt_ri: int | None = None
    schedulable: bool | None = None


@dataclass
class AnalysisResult:
    """Combined analysis outputs for DM RTA, EDF PDC, and EDF WCRT."""

    dm_rta_rows: list[DMRTARow] = field(default_factory=list)
    edf_pdc_summary: EDFPDCSummary | None = None
    edf_pdc_points: list[EDFPDCPoint] = field(default_factory=list)
    edf_wcrt_rows: list[EDFWCRTRow] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class SimJobRow:
    """Per-job simulation row."""

    task_id: str
    job_index: int
    release_time: int
    abs_deadline: int
    start_time: int | None = None
    finish_time: int | None = None
    response_time: int | None = None
    met_deadline: bool | None = None
    preemptions: int | None = None


@dataclass
class SimTaskRow:
    """Per-task simulation summary row."""

    task_id: str
    wcet_c: int
    period_t: int
    deadline_d: int
    jobs_simulated: int
    worst_response_time: float | None = None
    avg_response_time: float | None = None
    min_response_time: float | None = None
    deadline_misses: int | None = None
    preemptions_total: int | None = None
    rrj: float | None = None
    arj: float | None = None


@dataclass
class SimResult:
    """Simulation output container for one scheduling policy."""

    policy: str
    stop_time: int
    jobs: list[SimJobRow] = field(default_factory=list)
    task_rows: list[SimTaskRow] = field(default_factory=list)
    deadline_misses_total: int = 0


@dataclass
class CompareResult:
    """Comparison output rows for analysis-vs-simulation checks."""

    rows: list[dict[str, Any]] = field(default_factory=list)
