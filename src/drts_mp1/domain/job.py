"""Job-level runtime model used by the simulator."""

from __future__ import annotations

from dataclasses import dataclass

from .types import TaskID, Time


@dataclass
class Job:
    """Represents one released job of a task."""

    task_id: TaskID
    job_index: int
    release_time: Time
    abs_deadline: Time
    remaining_exec: Time
    start_time: Time | None = None
    finish_time: Time | None = None
    preemptions: int = 0
