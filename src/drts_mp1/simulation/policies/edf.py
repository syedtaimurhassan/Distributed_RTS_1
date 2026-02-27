"""Earliest Deadline First policy scaffold for single-core simulation."""

from __future__ import annotations

from collections.abc import Sequence

from drts_mp1.domain.job import Job
from drts_mp1.domain.types import Time
from drts_mp1.simulation.policies.base import SchedulerPolicy


class EDFPolicy(SchedulerPolicy):
    """Earliest Deadline First policy (shortest absolute deadline first)."""

    name = "edf"

    def pick_next(self, ready_jobs: Sequence[Job], now: Time) -> Job | None:
        if not ready_jobs:
            return None
        return min(
            ready_jobs,
            key=lambda job: (
                job.abs_deadline,
                job.task_id,
                job.job_index,
            ),
        )
