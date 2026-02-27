"""Unit test for EDF PDC/dbf using Buttazzo Table 4.4 parameters."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from drts_mp1.analysis.edf_pdc import check_edf_pdc
from drts_mp1.domain.task import Task
from drts_mp1.domain.taskset import TaskSet


class TestEDFPDCTable44(unittest.TestCase):
    """Validate EDF feasibility calculations against the textbook example."""

    def test_table_4_4_values_and_dbf_points(self) -> None:
        # Table 4.4 task set:
        # tau_1: C=2, T=6, D=4
        # tau_2: C=2, T=8, D=5
        # tau_3: C=3, T=9, D=7
        taskset = TaskSet(
            tasks=[
                Task(task_id="tau_1", jitter=0, bcet=2, wcet=2, period=6, deadline=4, pe=0),
                Task(task_id="tau_2", jitter=0, bcet=2, wcet=2, period=8, deadline=5, pe=0),
                Task(task_id="tau_3", jitter=0, bcet=3, wcet=3, period=9, deadline=7, pe=0),
            ]
        )

        result = check_edf_pdc(taskset)
        self.assertIsNotNone(result.edf_pdc_summary)
        summary = result.edf_pdc_summary
        assert summary is not None

        # U = 2/6 + 2/8 + 3/9 = 11/12
        self.assertEqual(summary.u_total, "11/12")
        # L* = 25 (exact)
        self.assertEqual(summary.l_star, "25")
        self.assertEqual(summary.h_hyperperiod, 72)
        self.assertEqual(summary.d_max, 7)
        self.assertEqual(summary.test_bound, 25)
        self.assertTrue(summary.feasible)

        points = [row.t for row in result.edf_pdc_points]
        self.assertEqual(points, [4, 5, 7, 10, 13, 16, 21, 22, 25])

        dbf_by_t = {row.t: row.dbf_t for row in result.edf_pdc_points}
        self.assertEqual(dbf_by_t[4], 2)
        self.assertEqual(dbf_by_t[5], 4)
        self.assertEqual(dbf_by_t[7], 7)
        self.assertEqual(dbf_by_t[10], 9)
        self.assertEqual(dbf_by_t[13], 11)
        self.assertEqual(dbf_by_t[16], 16)
        self.assertEqual(dbf_by_t[21], 18)
        self.assertEqual(dbf_by_t[22], 20)
        self.assertEqual(dbf_by_t[25], 23)

        self.assertTrue(all((row.passed is True) for row in result.edf_pdc_points))


if __name__ == "__main__":
    unittest.main()
