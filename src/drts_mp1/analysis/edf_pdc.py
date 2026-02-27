"""EDF feasibility analysis via processor-demand criterion / demand bound function.

References:
- Buttazzo, Chapter 4, Section 4.6.1: dbf(t) <= t
- Buttazzo, Chapter 4, Section 4.6.2 / Theorem 4.6: reduced test points
"""

from __future__ import annotations

from fractions import Fraction

from drts_mp1.analysis.math_utils import ceil_fraction, fraction_to_str, lcm_many
from drts_mp1.domain.results import AnalysisResult, EDFPDCPoint, EDFPDCSummary
from drts_mp1.domain.taskset import TaskSet


def compute_dbf(taskset: TaskSet, t: int) -> int:
    """Compute synchronous periodic-task demand bound function at time `t`.

    dbf(t) = sum_i floor((t + T_i - D_i) / T_i) * C_i
    with floor term clamped to 0 when negative.
    """
    demand = 0
    for task in taskset.tasks:
        jobs = (t + task.period - task.deadline) // task.period
        if jobs < 0:
            jobs = 0
        demand += jobs * task.wcet
    return demand


def _utilization_fraction(taskset: TaskSet) -> Fraction:
    u_total = Fraction(0, 1)
    for task in taskset.tasks:
        u_total += Fraction(task.wcet, task.period)
    return u_total


def _compute_l_star(taskset: TaskSet, u_total: Fraction) -> Fraction:
    weighted_sum = Fraction(0, 1)
    for task in taskset.tasks:
        u_i = Fraction(task.wcet, task.period)
        weighted_sum += (task.period - task.deadline) * u_i
    return weighted_sum / (Fraction(1, 1) - u_total)


def _generate_deadline_points(taskset: TaskSet, bound: int) -> list[int]:
    points: set[int] = set()
    for task in taskset.tasks:
        deadline = task.deadline
        while deadline <= bound:
            points.add(deadline)
            deadline += task.period
    return sorted(points)


def check_edf_pdc(taskset: TaskSet) -> AnalysisResult:
    """Check EDF feasibility by evaluating dbf at reduced absolute-deadline points."""
    if not taskset.tasks:
        summary = EDFPDCSummary(
            u_total=fraction_to_str(Fraction(0, 1)),
            h_hyperperiod=0,
            d_max=0,
            l_star=fraction_to_str(Fraction(0, 1)),
            test_bound=0,
            feasible=True,
        )
        return AnalysisResult(edf_pdc_summary=summary, edf_pdc_points=[])

    u_total = _utilization_fraction(taskset)
    h = lcm_many(task.period for task in taskset.tasks)
    d_max = max((task.deadline for task in taskset.tasks), default=0)

    if u_total >= 1:
        summary = EDFPDCSummary(
            u_total=fraction_to_str(u_total),
            h_hyperperiod=h,
            d_max=d_max,
            l_star=None,
            test_bound=None,
            feasible=False,
        )
        return AnalysisResult(edf_pdc_summary=summary, edf_pdc_points=[])

    l_star = _compute_l_star(taskset, u_total)
    test_bound = min(h, max(d_max, ceil_fraction(l_star)))
    test_points = _generate_deadline_points(taskset, test_bound)

    points: list[EDFPDCPoint] = []
    feasible = True
    for t in test_points:
        dbf_t = compute_dbf(taskset, t)
        passed = dbf_t <= t
        feasible = feasible and passed
        points.append(EDFPDCPoint(t=t, dbf_t=dbf_t, passed=passed))

    summary = EDFPDCSummary(
        u_total=fraction_to_str(u_total),
        h_hyperperiod=h,
        d_max=d_max,
        l_star=fraction_to_str(l_star),
        test_bound=test_bound,
        feasible=feasible,
    )
    return AnalysisResult(edf_pdc_summary=summary, edf_pdc_points=points)
