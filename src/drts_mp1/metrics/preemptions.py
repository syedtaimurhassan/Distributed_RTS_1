"""Preemption summary metrics computed from completed jobs."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from drts_mp1.domain.job import Job


def summarize_preemptions_by_task(completed_jobs: Iterable[Job]) -> dict[str, int]:
    """Aggregate preemption counts per task."""
    grouped: dict[str, int] = defaultdict(int)
    for job in completed_jobs:
        grouped[job.task_id] += job.preemptions
    return dict(grouped)
