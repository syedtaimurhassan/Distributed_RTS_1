"""Deadline Monotonic response-time analysis.

References:
- Buttazzo, Chapter 4, Section 4.5.2 (Eq. 4.17-4.19), iterative RTA.
"""

from __future__ import annotations

import math

from drts_mp1.analysis.priority import assign_dm_priorities
from drts_mp1.domain.results import AnalysisResult, DMRTARow
from drts_mp1.domain.task import Task
from drts_mp1.domain.taskset import TaskSet


def _compute_task_response_time(task: Task, higher_priority_tasks: list[Task]) -> tuple[int, bool, int]:
    """Compute one DM response time using iterative fixed-point recurrence.

    Recurrence:
    - R_0 = C_i
    - R_next = C_i + sum_{h<i} ceil(R_prev / T_h) * C_h

    Stop conditions:
    - Fixed point reached (`R_next == R_prev`)
    - Unschedulable early stop (`R_next > D_i`)
    """
    r_prev = task.wcet
    iterations = 0

    while True:
        interference = 0
        for hp_task in higher_priority_tasks:
            interference += math.ceil(r_prev / hp_task.period) * hp_task.wcet

        r_next = task.wcet + interference
        iterations += 1

        if r_next == r_prev:
            return r_next, r_next <= task.deadline, iterations

        if r_next > task.deadline:
            return r_next, False, iterations

        r_prev = r_next


def compute_dm_rta(taskset: TaskSet) -> AnalysisResult:
    """Compute DM per-task response-time bounds via iterative RTA."""
    prioritized_tasks = assign_dm_priorities(taskset)

    rows: list[DMRTARow] = []
    for index, task in enumerate(prioritized_tasks):
        higher_priority_tasks = prioritized_tasks[:index]
        r_i, schedulable, iterations = _compute_task_response_time(
            task=task,
            higher_priority_tasks=higher_priority_tasks,
        )
        rows.append(
            DMRTARow(
                task_id=task.task_id,
                wcet_c=task.wcet,
                period_t=task.period,
                deadline_d=task.deadline,
                priority_order=task.priority,
                rta_wcrt_ri=r_i,
                schedulable=schedulable,
                iterations=iterations,
            )
        )

    return AnalysisResult(dm_rta_rows=rows)
