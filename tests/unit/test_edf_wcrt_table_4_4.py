"""Unit test for exact EDF WCRT analysis against deterministic EDF simulation."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from drts_mp1.analysis.edf_wcrt import compute_edf_wcrt
from drts_mp1.domain.task import Task
from drts_mp1.domain.taskset import TaskSet
from drts_mp1.simulation.engine import run_simulation
from drts_mp1.simulation.policies.edf import EDFPolicy


class TestEDFWCRTTable44(unittest.TestCase):
    """Validate EDF analytical WCRT output on the Table 4.4 task parameters."""

    def test_edf_wcrt_matches_deterministic_simulation(self) -> None:
        taskset = TaskSet(
            tasks=[
                Task(task_id="tau_1", jitter=0, bcet=2, wcet=2, period=6, deadline=4, pe=0),
                Task(task_id="tau_2", jitter=0, bcet=2, wcet=2, period=8, deadline=5, pe=0),
                Task(task_id="tau_3", jitter=0, bcet=3, wcet=3, period=9, deadline=7, pe=0),
            ]
        )

        analysis = compute_edf_wcrt(taskset)
        hyperperiod = taskset.hyperperiod()
        sim = run_simulation(
            taskset=taskset,
            policy=EDFPolicy(),
            stop_time=hyperperiod,
            execution_time_mode="wcet",
            drain_after_stop=True,
        )

        sim_by_task = {row.task_id: row for row in sim.task_rows}
        self.assertEqual(len(analysis.edf_wcrt_rows), 3)

        for row in analysis.edf_wcrt_rows:
            self.assertIn(row.task_id, sim_by_task)
            sim_row = sim_by_task[row.task_id]
            self.assertIsNotNone(row.edf_wcrt_ri)
            self.assertIsNotNone(sim_row.worst_response_time)
            assert row.edf_wcrt_ri is not None
            assert sim_row.worst_response_time is not None
            self.assertEqual(float(row.edf_wcrt_ri), float(sim_row.worst_response_time))
            self.assertEqual(row.schedulable, row.edf_wcrt_ri <= row.deadline_d)


if __name__ == "__main__":
    unittest.main()
