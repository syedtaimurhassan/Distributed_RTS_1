"""Simulation event definitions for discrete-event scaffolding."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .types import JobID, Time


class EventType(str, Enum):
    """Supported event types for the future discrete-event simulator."""

    JOB_RELEASE = "JOB_RELEASE"
    JOB_COMPLETE = "JOB_COMPLETE"


@dataclass(order=True)
class Event:
    """A time-ordered simulation event."""

    time: Time
    type: EventType = field(compare=False)
    job_id: JobID | None = field(default=None, compare=False)
