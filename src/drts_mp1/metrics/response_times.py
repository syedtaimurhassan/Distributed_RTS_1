"""Response-time metrics computed from completed jobs."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from drts_mp1.domain.job import Job


def compute_response_times_by_task(completed_jobs: Iterable[Job]) -> dict[str, list[int]]:
    """Return response-time samples grouped by TaskID and ordered by job index."""
    grouped: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for job in completed_jobs:
        if job.finish_time is None:
            continue
        response_time = job.finish_time - job.release_time
        grouped[job.task_id].append((job.job_index, response_time))

    ordered: dict[str, list[int]] = {}
    for task_id, indexed_values in grouped.items():
        indexed_values.sort(key=lambda pair: pair[0])
        ordered[task_id] = [value for _, value in indexed_values]
    return ordered
