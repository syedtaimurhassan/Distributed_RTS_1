"""Release-response jitter metrics placeholders (RRJ/ARJ)."""

from __future__ import annotations

from collections.abc import Mapping


def compute_rrj_arj(
    response_times_by_task: Mapping[str, list[int]],
) -> dict[str, tuple[float | None, float | None]]:
    """Compute RRJ and ARJ per task.

    Definitions:
    - RRJ_i = max_k |R_{i,k+1} - R_{i,k}|
    - ARJ_i = max_k R_{i,k} - min_k R_{i,k}
    """
    metrics: dict[str, tuple[float | None, float | None]] = {}
    for task_id, samples in response_times_by_task.items():
        if not samples:
            metrics[task_id] = (None, None)
            continue

        if len(samples) == 1:
            metrics[task_id] = (0.0, 0.0)
            continue

        rrj = float(max(abs(curr - prev) for prev, curr in zip(samples, samples[1:])))
        arj = float(max(samples) - min(samples))
        metrics[task_id] = (rrj, arj)

    return metrics
