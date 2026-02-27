"""Priority queue wrapper for time-ordered simulation events."""

from __future__ import annotations

import heapq
from itertools import count

from drts_mp1.domain.events import Event, EventType


class EventQueue:
    """A min-heap queue ordered by event time."""

    def __init__(self) -> None:
        self._heap: list[tuple[int, int, Event]] = []
        self._counter = count()

    def push(self, event: Event) -> None:
        heapq.heappush(self._heap, (event.time, next(self._counter), event))

    def push_release(self, task_id: str, release_time: int) -> None:
        """Push a release event for the given task ID and release time."""
        self.push(Event(time=release_time, type=EventType.JOB_RELEASE, job_id=task_id))

    def pop(self) -> Event:
        return heapq.heappop(self._heap)[2]

    def pop_all_at(self, event_time: int) -> list[Event]:
        """Pop and return all events at the given time."""
        events: list[Event] = []
        while self._heap and self._heap[0][0] == event_time:
            events.append(self.pop())
        return events

    def peek(self) -> Event | None:
        if not self._heap:
            return None
        return self._heap[0][2]

    def next_time(self) -> int | None:
        """Return the next event time in the queue, or None if empty."""
        if not self._heap:
            return None
        return self._heap[0][0]

    def __len__(self) -> int:
        return len(self._heap)

    def __bool__(self) -> bool:
        return bool(self._heap)
