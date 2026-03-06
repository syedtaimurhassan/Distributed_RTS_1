"""End-to-end run test using Buttazzo Table 4.4 parameters."""

from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from drts_mp1.orchestration.run_one import run_one
from drts_mp1.orchestration.run_batch import run_batch


class TestE2ERunOnTable44(unittest.TestCase):
    """Validate orchestration outputs and key analysis values on a known task set."""

    def test_run_one_generates_expected_csvs_and_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            input_csv = tmp_path / "table_4_4.csv"
            out_root = tmp_path / "results" / "runs"

            input_csv.write_text(
                "\n".join(
                    [
                        "TaskID,Jitter,BCET,WCET,Period,Deadline,PE",
                        "tau_1,0,2,2,6,4,0",
                        "tau_2,0,2,2,8,5,0",
                        "tau_3,0,3,3,9,7,0",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            run_info = run_one(
                taskset_csv_path=input_csv,
                policies=["rm", "dm", "edf"],
                stop_rule="H",
                out_root=out_root,
                k=1,
            )

            run_dir = Path(str(run_info["run_dir"]))
            expected_files = [
                "run_metadata.csv",
                "input_taskset.csv",
                "analysis_dm_rta.csv",
                "analysis_edf_pdc_summary.csv",
                "analysis_edf_pdc_points.csv",
                "analysis_edf_wcrt.csv",
                "sim_jobs_rm.csv",
                "sim_jobs_dm.csv",
                "sim_jobs_edf.csv",
                "sim_tasks_rm.csv",
                "sim_tasks_dm.csv",
                "sim_tasks_edf.csv",
                "compare_dm_rta_vs_sim_dm.csv",
                "compare_edf_pdc_vs_sim_edf.csv",
                "compare_edf_wcrt_vs_sim_edf.csv",
            ]
            for filename in expected_files:
                self.assertTrue((run_dir / filename).exists(), msg=f"missing {filename}")

            with (run_dir / "analysis_edf_pdc_summary.csv").open(
                "r", newline="", encoding="utf-8"
            ) as handle:
                row = next(csv.DictReader(handle))
            self.assertEqual(row["U_total"], "11/12")
            self.assertEqual(row["H_hyperperiod"], "72")
            self.assertEqual(row["D_max"], "7")
            self.assertEqual(row["L_star"], "25")
            self.assertEqual(row["TestBound"], "25")
            self.assertEqual(row["Feasible"], "True")

            with (run_dir / "analysis_dm_rta.csv").open(
                "r", newline="", encoding="utf-8"
            ) as handle:
                dm_rows = list(csv.DictReader(handle))

            dm_by_task = {row["TaskID"]: row for row in dm_rows}
            self.assertEqual(dm_by_task["tau_3"]["RTA_WCRT_Ri"], "9")
            self.assertEqual(dm_by_task["tau_3"]["Schedulable"], "False")

            with (run_dir / "compare_edf_pdc_vs_sim_edf.csv").open(
                "r", newline="", encoding="utf-8"
            ) as handle:
                compare_row = next(csv.DictReader(handle))
            self.assertEqual(compare_row["EDF_PDC_Feasible"], "True")
            self.assertEqual(compare_row["Agreement"], "True")

            with (run_dir / "compare_edf_wcrt_vs_sim_edf.csv").open(
                "r", newline="", encoding="utf-8"
            ) as handle:
                compare_wcrt_rows = list(csv.DictReader(handle))
            self.assertEqual(len(compare_wcrt_rows), 3)
            self.assertTrue(all(row["Difference"] == "0.0" for row in compare_wcrt_rows))

    def test_batch_recursive_discovery_writes_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            nested_input_dir = tmp_path / "inputs" / "nested"
            nested_input_dir.mkdir(parents=True, exist_ok=True)
            input_csv = nested_input_dir / "table_4_4.csv"
            out_root = tmp_path / "results" / "runs"

            input_csv.write_text(
                "\n".join(
                    [
                        "TaskID,Jitter,BCET,WCET,Period,Deadline,PE",
                        "tau_1,0,2,2,6,4,0",
                        "tau_2,0,2,2,8,5,0",
                        "tau_3,0,3,3,9,7,0",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            entries = run_batch(
                input_dir=tmp_path / "inputs",
                policies=["rm", "dm", "edf"],
                stop_rule="H",
                out_root=out_root,
                k=1,
            )

            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["status"], "success")

            manifest_path = out_root / "batch_manifest.csv"
            self.assertTrue(manifest_path.exists())
            with manifest_path.open("r", newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["status"], "success")
            self.assertEqual(rows[0]["input_file"], str(input_csv.resolve()))


if __name__ == "__main__":
    unittest.main()
