"""Discrete-event simulation engine for single-core preemptive scheduling."""

from __future__ import annotations

from collections import defaultdict

from drts_mp1.domain.job import Job
from drts_mp1.domain.results import SimJobRow, SimResult
from drts_mp1.domain.task import Task
from drts_mp1.domain.taskset import TaskSet
from drts_mp1.domain.types import Time
from drts_mp1.metrics.summarize import build_task_summary_rows
from drts_mp1.simulation.event_queue import EventQueue
from drts_mp1.simulation.policies.base import SchedulerPolicy
from drts_mp1.simulation.state import SimulationState


def _build_release_queue(taskset: TaskSet, stop_time: int) -> EventQueue:
    queue = EventQueue()
    for task in sorted(taskset.tasks, key=lambda item: item.task_id):
        release_time = 0
        while release_time < stop_time:
            queue.push_release(task_id=task.task_id, release_time=release_time)
            release_time += task.period
    return queue


def _complete_job(state: SimulationState, job: Job) -> None:
    job.finish_time = state.now
    state.completed_jobs.append(job)
    if job.finish_time > job.abs_deadline:
        state.deadline_misses += 1


def _dispatch(state: SimulationState, policy: SchedulerPolicy) -> None:
    contenders: list[Job] = []
    if state.running_job is not None:
        contenders.append(state.running_job)
    contenders.extend(state.ready_jobs)

    selected = policy.pick_next(contenders, state.now)
    if selected is None:
        state.running_job = None
        return

    if state.running_job is not None and selected is state.running_job:
        return

    if state.running_job is not None and selected is not state.running_job:
        state.running_job.preemptions += 1
        state.ready_jobs.append(state.running_job)

    if selected in state.ready_jobs:
        state.ready_jobs.remove(selected)

    state.running_job = selected
    if state.running_job.start_time is None:
        state.running_job.start_time = state.now


def _process_releases(
    state: SimulationState,
    release_queue: EventQueue,
    task_by_id: dict[str, Task],
    next_job_index: dict[str, int],
) -> None:
    for event in release_queue.pop_all_at(state.now):
        task_id = event.job_id
        if task_id is None:
            continue

        task = task_by_id[task_id]
        job = Job(
            task_id=task.task_id,
            job_index=next_job_index[task.task_id],
            release_time=state.now,
            abs_deadline=state.now + task.deadline,
            remaining_exec=task.wcet,
        )
        next_job_index[task.task_id] += 1
        state.released_jobs.append(job)

        if job.remaining_exec == 0:
            job.start_time = state.now
            _complete_job(state, job)
        else:
            state.ready_jobs.append(job)


def _to_sim_job_rows(jobs: list[Job]) -> list[SimJobRow]:
    rows: list[SimJobRow] = []
    for job in sorted(jobs, key=lambda item: (item.release_time, item.task_id, item.job_index)):
        if job.finish_time is None:
            response_time: int | None = None
            met_deadline: bool | None = None
        else:
            response_time = job.finish_time - job.release_time
            met_deadline = job.finish_time <= job.abs_deadline
        rows.append(
            SimJobRow(
                task_id=job.task_id,
                job_index=job.job_index,
                release_time=job.release_time,
                abs_deadline=job.abs_deadline,
                start_time=job.start_time,
                finish_time=job.finish_time,
                response_time=response_time,
                met_deadline=met_deadline,
                preemptions=job.preemptions,
            )
        )
    return rows


def run_simulation(taskset: TaskSet, policy: SchedulerPolicy, stop_time: Time) -> SimResult:
    """Run discrete-event simulation to `stop_time` using the selected policy."""
    stop = int(stop_time)
    state = SimulationState(now=0)
    task_by_id = {task.task_id: task for task in taskset.tasks}
    next_job_index: dict[str, int] = defaultdict(int)
    release_queue = _build_release_queue(taskset=taskset, stop_time=stop)

    policy.configure(taskset)

    while True:
        if state.running_job is None and not state.ready_jobs:
            next_release = release_queue.next_time()
            if next_release is None or next_release >= stop:
                break
            state.now = next_release
            _process_releases(state, release_queue, task_by_id, next_job_index)
            _dispatch(state, policy)
            continue

        if state.running_job is None and state.ready_jobs:
            _dispatch(state, policy)
            if state.running_job is None:
                break

        next_release_time = release_queue.next_time()
        assert state.running_job is not None
        completion_time = state.now + state.running_job.remaining_exec
        next_time = completion_time
        if next_release_time is not None and next_release_time < next_time:
            next_time = next_release_time

        if next_time > stop:
            if state.running_job is not None:
                state.running_job.remaining_exec -= stop - state.now
            state.now = stop
            break

        elapsed = next_time - state.now
        if elapsed > 0 and state.running_job is not None:
            state.running_job.remaining_exec -= elapsed
        state.now = next_time

        if state.running_job is not None and state.running_job.remaining_exec == 0:
            _complete_job(state, state.running_job)
            state.running_job = None

        if release_queue.next_time() == state.now:
            _process_releases(state, release_queue, task_by_id, next_job_index)

        _dispatch(state, policy)

    completed_jobs = list(state.completed_jobs)
    task_rows = build_task_summary_rows(taskset=taskset, completed_jobs=completed_jobs)
    job_rows = _to_sim_job_rows(completed_jobs)

    return SimResult(
        policy=policy.name,
        stop_time=stop,
        jobs=job_rows,
        task_rows=task_rows,
        deadline_misses_total=state.deadline_misses,
    )
