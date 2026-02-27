"""Mutable simulation state used by the event-driven engine."""

from __future__ import annotations

from dataclasses import dataclass, field

from drts_mp1.domain.job import Job


@dataclass
class SimulationState:
    """Single-core simulation state snapshot."""

    now: int = 0
    ready_jobs: list[Job] = field(default_factory=list)
    running_job: Job | None = None
    released_jobs: list[Job] = field(default_factory=list)
    completed_jobs: list[Job] = field(default_factory=list)
    deadline_misses: int = 0
