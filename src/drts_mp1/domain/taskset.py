"""TaskSet container and derived properties such as utilization/hyperperiod."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .task import Task


@dataclass
class TaskSet:
    """Collection of tasks with convenience methods for analysis and simulation."""

    tasks: list[Task] = field(default_factory=list)

    def utilization(self) -> float:
        """Return total utilization sum(C_i / T_i)."""
        if not self.tasks:
            return 0.0
        return sum(task.wcet / task.period for task in self.tasks)

    def hyperperiod(self) -> int:
        """Return LCM of all task periods; 0 when the task set is empty."""
        periods = [task.period for task in self.tasks if task.period > 0]
        if not periods:
            return 0
        h = periods[0]
        for period in periods[1:]:
            h = math.lcm(h, period)
        return h

    def sorted_by_deadline(self) -> list[Task]:
        """Return tasks ordered by non-decreasing relative deadline."""
        return sorted(self.tasks, key=lambda task: (task.deadline, task.task_id))

    def sorted_by_period(self) -> list[Task]:
        """Return tasks ordered by non-decreasing period."""
        return sorted(self.tasks, key=lambda task: (task.period, task.task_id))
