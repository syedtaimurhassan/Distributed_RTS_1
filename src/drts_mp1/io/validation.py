"""Validation helpers for task-set CSV parsing and semantic checks."""

from __future__ import annotations

from collections.abc import Iterable

from drts_mp1.domain.taskset import TaskSet

REQUIRED_TASKSET_COLUMNS: tuple[str, ...] = (
    "TaskID",
    "Jitter",
    "BCET",
    "WCET",
    "Period",
    "Deadline",
    "PE",
)
OPTIONAL_TASKSET_COLUMNS: tuple[str, ...] = ("Priority",)


def validate_required_columns(fieldnames: Iterable[str] | None) -> None:
    """Ensure all required CSV columns are available."""
    if fieldnames is None:
        raise ValueError("Input CSV is missing a header row.")

    provided = set(fieldnames)
    missing = [name for name in REQUIRED_TASKSET_COLUMNS if name not in provided]
    if missing:
        raise ValueError(f"Input CSV missing required columns: {', '.join(missing)}")


def parse_int(value: str, column: str, row_index: int) -> int:
    """Convert a CSV value into int with context-rich errors."""
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Invalid integer in column '{column}' at row {row_index}: {value!r}"
        ) from exc


def validate_taskset(taskset: TaskSet) -> list[str]:
    """Validate task-level constraints for constrained-deadline systems.

    Raises:
    - ValueError: invalid timing parameters.

    Returns:
    - List of non-fatal warnings.
    """
    warnings: list[str] = []

    for task in taskset.tasks:
        if task.wcet < 0:
            raise ValueError(f"Task {task.task_id}: WCET must be >= 0.")
        if task.period <= 0:
            raise ValueError(f"Task {task.task_id}: Period must be > 0.")
        if task.deadline <= 0:
            raise ValueError(f"Task {task.task_id}: Deadline must be > 0.")
        if task.deadline > task.period:
            raise ValueError(
                f"Task {task.task_id}: Deadline must be <= Period for constrained deadlines."
            )
        if task.bcet < 0:
            warnings.append(f"Task {task.task_id}: BCET is negative; check source CSV.")
        if task.bcet > task.wcet:
            warnings.append(
                f"Task {task.task_id}: BCET > WCET; check task-set assumptions."
            )

    return warnings
