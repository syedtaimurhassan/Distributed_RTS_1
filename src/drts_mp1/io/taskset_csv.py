"""CSV reader for task sets provided by the course resources."""

from __future__ import annotations

import csv
from pathlib import Path

from drts_mp1.domain.task import Task
from drts_mp1.domain.taskset import TaskSet
from drts_mp1.io.validation import (
    OPTIONAL_TASKSET_COLUMNS,
    parse_int,
    validate_required_columns,
    validate_taskset,
)


def read_taskset_csv(path: str | Path) -> TaskSet:
    """Read a task-set CSV into `TaskSet`.

    Notes:
    - Required schema: TaskID,Jitter,BCET,WCET,Period,Deadline,PE
    - Optional column: Priority
    - `PE` is preserved in Task objects but ignored in single-core logic.
    """
    csv_path = Path(path)
    tasks: list[Task] = []

    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        validate_required_columns(reader.fieldnames)

        has_priority = (
            reader.fieldnames is not None
            and OPTIONAL_TASKSET_COLUMNS[0] in set(reader.fieldnames)
        )

        for row_index, row in enumerate(reader, start=2):
            task_id = str(row["TaskID"]).strip()
            jitter = parse_int(row["Jitter"], "Jitter", row_index)
            bcet = parse_int(row["BCET"], "BCET", row_index)
            wcet = parse_int(row["WCET"], "WCET", row_index)
            period = parse_int(row["Period"], "Period", row_index)
            deadline = parse_int(row["Deadline"], "Deadline", row_index)
            pe = parse_int(row["PE"], "PE", row_index)

            priority: int | None = None
            if has_priority:
                raw_priority = (row.get("Priority") or "").strip()
                if raw_priority:
                    priority = parse_int(raw_priority, "Priority", row_index)

            tasks.append(
                Task(
                    task_id=task_id,
                    jitter=jitter,
                    bcet=bcet,
                    wcet=wcet,
                    period=period,
                    deadline=deadline,
                    pe=pe,
                    priority=priority,
                )
            )

    taskset = TaskSet(tasks=tasks)
    validate_taskset(taskset)
    return taskset
