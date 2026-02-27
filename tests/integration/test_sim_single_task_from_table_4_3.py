"""Integration test for discrete-event simulation with Table 4.3 tau_1."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from drts_mp1.domain.task import Task
from drts_mp1.domain.taskset import TaskSet
from drts_mp1.simulation.engine import run_simulation
from drts_mp1.simulation.policies.rm import RMPolicy


class TestSimSingleTaskTable43(unittest.TestCase):
    """Validate release/completion/deadline behavior for a single periodic task."""

    def test_single_task_rm_schedule(self) -> None:
        # Table 4.3 tau_1: C=1, T=4, D=3.
        taskset = TaskSet(
            tasks=[
                Task(
                    task_id="tau_1",
                    jitter=0,
                    bcet=1,
                    wcet=1,
                    period=4,
                    deadline=3,
                    pe=0,
                )
            ]
        )

        result = run_simulation(taskset=taskset, policy=RMPolicy(), stop_time=16)

        self.assertEqual(len(result.jobs), 4)
        self.assertEqual(result.deadline_misses_total, 0)

        for index, row in enumerate(result.jobs):
            expected_release = index * 4
            expected_finish = expected_release + 1
            expected_deadline = expected_release + 3

            self.assertEqual(row.task_id, "tau_1")
            self.assertEqual(row.job_index, index)
            self.assertEqual(row.release_time, expected_release)
            self.assertEqual(row.start_time, expected_release)
            self.assertEqual(row.finish_time, expected_finish)
            self.assertEqual(row.abs_deadline, expected_deadline)
            self.assertEqual(row.response_time, 1)
            self.assertTrue(row.met_deadline)
            self.assertEqual(row.preemptions, 0)

        self.assertEqual(len(result.task_rows), 1)
        summary = result.task_rows[0]
        self.assertEqual(summary.task_id, "tau_1")
        self.assertEqual(summary.jobs_simulated, 4)
        self.assertEqual(summary.worst_response_time, 1.0)
        self.assertEqual(summary.avg_response_time, 1.0)
        self.assertEqual(summary.min_response_time, 1.0)
        self.assertEqual(summary.deadline_misses, 0)
        self.assertEqual(summary.preemptions_total, 0)
        self.assertEqual(summary.rrj, 0.0)
        self.assertEqual(summary.arj, 0.0)


if __name__ == "__main__":
    unittest.main()
