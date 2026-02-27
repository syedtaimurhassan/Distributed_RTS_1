"""Integration test that parses the provided task-set-example.csv."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from drts_mp1.io.taskset_csv import read_taskset_csv


def test_parse_existing_example_csv() -> None:
    csv_path = ROOT / "task-set-example.csv"
    taskset = read_taskset_csv(csv_path)

    assert len(taskset.tasks) > 0

    for task in taskset.tasks:
        assert isinstance(task.wcet, int)
        assert isinstance(task.period, int)
        assert isinstance(task.deadline, int)
        assert task.deadline <= task.period
