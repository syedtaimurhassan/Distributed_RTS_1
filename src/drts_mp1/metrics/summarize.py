"""Build per-task simulation summary rows from completed jobs."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from drts_mp1.domain.job import Job
from drts_mp1.domain.results import SimTaskRow
from drts_mp1.domain.taskset import TaskSet
from drts_mp1.metrics.jitter import compute_rrj_arj
from drts_mp1.metrics.preemptions import summarize_preemptions_by_task
from drts_mp1.metrics.response_times import compute_response_times_by_task


def build_task_summary_rows(taskset: TaskSet, completed_jobs: Iterable[Job]) -> list[SimTaskRow]:
    """Create per-task summary rows from completed job traces.

    This helper is simulation-independent and can be reused for future runs.
    """
    jobs = list(completed_jobs)
    completed_by_task: dict[str, list[Job]] = defaultdict(list)
    for job in jobs:
        completed_by_task[job.task_id].append(job)

    response_times_by_task = compute_response_times_by_task(jobs)
    preemptions_by_task = summarize_preemptions_by_task(jobs)
    jitter_by_task = compute_rrj_arj(response_times_by_task)

    rows: list[SimTaskRow] = []
    for task in taskset.tasks:
        samples = response_times_by_task.get(task.task_id, [])
        rrj, arj = jitter_by_task.get(task.task_id, (None, None))
        job_count = len(samples)
        completed_for_task = completed_by_task.get(task.task_id, [])

        if samples:
            worst_rt: float | None = float(max(samples))
            avg_rt: float | None = float(sum(samples) / len(samples))
            min_rt: float | None = float(min(samples))
            deadline_misses = sum(
                1
                for job in completed_for_task
                if job.finish_time is not None and job.finish_time > job.abs_deadline
            )
            preemptions_total = preemptions_by_task.get(task.task_id, 0)
        else:
            worst_rt = None
            avg_rt = None
            min_rt = None
            deadline_misses = 0
            preemptions_total = 0

        rows.append(
            SimTaskRow(
                task_id=task.task_id,
                wcet_c=task.wcet,
                period_t=task.period,
                deadline_d=task.deadline,
                jobs_simulated=job_count,
                worst_response_time=worst_rt,
                avg_response_time=avg_rt,
                min_response_time=min_rt,
                deadline_misses=deadline_misses,
                preemptions_total=preemptions_total,
                rrj=rrj,
                arj=arj,
            )
        )

    return rows
