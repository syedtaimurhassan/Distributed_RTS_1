"""Task model matching the course CSV schema."""

from __future__ import annotations

from dataclasses import dataclass

from .types import Priority, TaskID


@dataclass(frozen=True)
class Task:
    """Periodic/sporadic task parameters from input CSV.

    Assumptions:
    - Fields mirror task-set CSV columns from course resources.
    - `pe` is parsed and stored, but ignored by single-core scheduling logic.
    """

    task_id: TaskID
    jitter: int
    bcet: int
    wcet: int
    period: int
    deadline: int
    pe: int | None = None
    priority: Priority | None = None
