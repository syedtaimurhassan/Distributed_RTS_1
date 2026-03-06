"""Exact EDF WCRT analysis for synchronous periodic task sets.

References:
- Mini-project requirement PDF section "A Worst-Case Response Time Analysis for EDF"
- Buttazzo Chapter 4 (EDF priority rule and response-time definition)
"""

from __future__ import annotations

from collections import defaultdict

from drts_mp1.domain.job import Job
from drts_mp1.domain.results import AnalysisResult, EDFWCRTRow
from drts_mp1.domain.taskset import TaskSet


def _pick_earliest_deadline(jobs: list[Job]) -> Job | None:
    if not jobs:
        return None
    return min(
        jobs,
        key=lambda job: (
            job.abs_deadline,
            job.task_id,
            job.job_index,
        ),
    )


def _generate_jobs_for_hyperperiod(taskset: TaskSet, hyperperiod: int) -> list[Job]:
    jobs: list[Job] = []
    for task in sorted(taskset.tasks, key=lambda item: item.task_id):
        job_index = 0
        release_time = 0
        while release_time < hyperperiod:
            jobs.append(
                Job(
                    task_id=task.task_id,
                    job_index=job_index,
                    release_time=release_time,
                    abs_deadline=release_time + task.deadline,
                    remaining_exec=task.wcet,
                )
            )
            job_index += 1
            release_time += task.period

    jobs.sort(key=lambda job: (job.release_time, job.task_id, job.job_index))
    return jobs


def _admit_releases_at(
    now: int,
    generated_jobs: list[Job],
    release_index: int,
    ready_jobs: list[Job],
    completed_jobs: list[Job],
) -> int:
    """Move jobs released at `now` into ready/completed lists and return new index."""
    index = release_index
    while index < len(generated_jobs) and generated_jobs[index].release_time == now:
        job = generated_jobs[index]
        if job.remaining_exec == 0:
            job.start_time = now
            job.finish_time = now
            completed_jobs.append(job)
        else:
            ready_jobs.append(job)
        index += 1
    return index


def _dispatch_edf(now: int, ready_jobs: list[Job], running_job: Job | None) -> Job | None:
    contenders: list[Job] = list(ready_jobs)
    if running_job is not None:
        contenders.append(running_job)

    selected = _pick_earliest_deadline(contenders)
    if selected is None:
        return None

    if running_job is not None and selected is running_job:
        return running_job

    if running_job is not None and selected is not running_job:
        running_job.preemptions += 1
        ready_jobs.append(running_job)

    if selected in ready_jobs:
        ready_jobs.remove(selected)

    if selected.start_time is None:
        selected.start_time = now
    return selected


def compute_edf_wcrt(taskset: TaskSet) -> AnalysisResult:
    """Compute exact per-task EDF WCRTs for synchronous periodic WCET execution.

    Procedure:
    - Build all jobs released in `[0, H)`, where `H` is the hyperperiod.
    - Simulate preemptive single-core EDF with WCET execution for each job.
    - Compute `R_{i,k} = f_{i,k} - r_{i,k}` and `WCRT_i = max_k R_{i,k}`.
    """
    hyperperiod = taskset.hyperperiod()
    generated_jobs = _generate_jobs_for_hyperperiod(taskset, hyperperiod)

    ready_jobs: list[Job] = []
    completed_jobs: list[Job] = []
    release_index = 0
    now = 0
    running_job: Job | None = None

    while release_index < len(generated_jobs) or running_job is not None or ready_jobs:
        if running_job is None and not ready_jobs:
            if release_index >= len(generated_jobs):
                break
            now = generated_jobs[release_index].release_time
            release_index = _admit_releases_at(
                now=now,
                generated_jobs=generated_jobs,
                release_index=release_index,
                ready_jobs=ready_jobs,
                completed_jobs=completed_jobs,
            )
            running_job = _dispatch_edf(now=now, ready_jobs=ready_jobs, running_job=running_job)
            continue

        if running_job is None:
            running_job = _dispatch_edf(now=now, ready_jobs=ready_jobs, running_job=running_job)
            if running_job is None:
                continue

        next_release_time = (
            generated_jobs[release_index].release_time
            if release_index < len(generated_jobs)
            else None
        )
        completion_time = now + running_job.remaining_exec
        next_time = completion_time
        if next_release_time is not None and next_release_time < next_time:
            next_time = next_release_time

        elapsed = next_time - now
        if elapsed > 0:
            running_job.remaining_exec -= elapsed
        now = next_time

        if running_job.remaining_exec == 0:
            running_job.finish_time = now
            completed_jobs.append(running_job)
            running_job = None

        if next_release_time is not None and next_release_time == now:
            release_index = _admit_releases_at(
                now=now,
                generated_jobs=generated_jobs,
                release_index=release_index,
                ready_jobs=ready_jobs,
                completed_jobs=completed_jobs,
            )

        running_job = _dispatch_edf(now=now, ready_jobs=ready_jobs, running_job=running_job)

    response_times_by_task: dict[str, list[int]] = defaultdict(list)
    jobs_in_hyperperiod_by_task: dict[str, int] = defaultdict(int)
    for job in generated_jobs:
        jobs_in_hyperperiod_by_task[job.task_id] += 1
    for job in completed_jobs:
        if job.finish_time is None:
            continue
        response_times_by_task[job.task_id].append(job.finish_time - job.release_time)

    rows: list[EDFWCRTRow] = []
    for task in sorted(taskset.tasks, key=lambda item: item.task_id):
        samples = response_times_by_task.get(task.task_id, [])
        if samples:
            wcrt = max(samples)
            schedulable = wcrt <= task.deadline
        else:
            wcrt = None
            schedulable = None

        rows.append(
            EDFWCRTRow(
                task_id=task.task_id,
                wcet_c=task.wcet,
                period_t=task.period,
                deadline_d=task.deadline,
                jobs_in_hyperperiod=jobs_in_hyperperiod_by_task.get(task.task_id, 0),
                edf_wcrt_ri=wcrt,
                schedulable=schedulable,
            )
        )

    return AnalysisResult(edf_wcrt_rows=rows)
