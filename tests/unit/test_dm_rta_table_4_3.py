"""Unit test for DM RTA using Buttazzo Table 4.3 parameters."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from drts_mp1.analysis.dm_rta import compute_dm_rta
from drts_mp1.domain.task import Task
from drts_mp1.domain.taskset import TaskSet


class TestDMRTATable43(unittest.TestCase):
    """Validate Eq. (4.17)-(4.19) iteration behavior on Table 4.3 data."""

    def test_tau4_response_time_matches_reference(self) -> None:
        taskset = TaskSet(
            tasks=[
                Task(task_id="tau_1", jitter=0, bcet=1, wcet=1, period=4, deadline=3, pe=0),
                Task(task_id="tau_2", jitter=0, bcet=1, wcet=1, period=5, deadline=4, pe=0),
                Task(task_id="tau_3", jitter=0, bcet=2, wcet=2, period=6, deadline=5, pe=0),
                Task(task_id="tau_4", jitter=0, bcet=1, wcet=1, period=11, deadline=10, pe=0),
            ]
        )

        result = compute_dm_rta(taskset)
        by_task = {row.task_id: row for row in result.dm_rta_rows}

        self.assertIn("tau_4", by_task)
        tau4 = by_task["tau_4"]

        self.assertEqual(tau4.rta_wcrt_ri, 10)
        self.assertTrue(tau4.schedulable)
        self.assertEqual(tau4.iterations, 6)


if __name__ == "__main__":
    unittest.main()
