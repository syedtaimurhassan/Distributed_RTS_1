"""Priority assignment helpers for fixed-priority schedulers."""

from __future__ import annotations

from dataclasses import replace

from drts_mp1.domain.task import Task
from drts_mp1.domain.taskset import TaskSet


def assign_rm_priorities(taskset: TaskSet) -> list[Task]:
    """Assign Rate Monotonic priorities (shorter period => higher priority)."""
    ordered = sorted(taskset.tasks, key=lambda task: (task.period, task.task_id))
    return [replace(task, priority=index + 1) for index, task in enumerate(ordered)]


def assign_dm_priorities(taskset: TaskSet) -> list[Task]:
    """Assign Deadline Monotonic priorities (shorter deadline => higher priority).

    Tie-breaker:
    - When deadlines are equal, order by `TaskID` using string comparison.
    """
    ordered = sorted(taskset.tasks, key=lambda task: (task.deadline, task.task_id))
    return [replace(task, priority=index + 1) for index, task in enumerate(ordered)]
