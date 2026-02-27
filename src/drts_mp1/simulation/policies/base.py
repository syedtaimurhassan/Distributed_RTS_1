"""Base scheduler policy protocol for the simulation engine."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from drts_mp1.domain.job import Job
from drts_mp1.domain.task import Task
from drts_mp1.domain.taskset import TaskSet
from drts_mp1.domain.types import Time


class SchedulerPolicy(ABC):
    """Base policy interface used by the simulator."""

    name: str = "base"

    def __init__(self) -> None:
        self._task_by_id: dict[str, Task] = {}

    def configure(self, taskset: TaskSet) -> None:
        """Bind task parameters so policies can evaluate priorities."""
        self._task_by_id = {task.task_id: task for task in taskset.tasks}

    def task_period(self, task_id: str) -> int:
        task = self._task_by_id.get(task_id)
        if task is None:
            return 2**31 - 1
        return task.period

    def task_deadline(self, task_id: str) -> int:
        task = self._task_by_id.get(task_id)
        if task is None:
            return 2**31 - 1
        return task.deadline

    @abstractmethod
    def pick_next(self, ready_jobs: Sequence[Job], now: Time) -> Job | None:
        """Choose the next job to run at `now`."""
        raise NotImplementedError
