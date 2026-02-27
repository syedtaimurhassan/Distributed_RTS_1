"""Smoke test ensuring all scaffold modules import successfully."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

MODULES = [
    "drts_mp1.domain.task",
    "drts_mp1.domain.taskset",
    "drts_mp1.domain.job",
    "drts_mp1.domain.events",
    "drts_mp1.domain.results",
    "drts_mp1.domain.types",
    "drts_mp1.io.taskset_csv",
    "drts_mp1.io.validation",
    "drts_mp1.io.output_csv",
    "drts_mp1.io.paths",
    "drts_mp1.analysis.dm_rta",
    "drts_mp1.analysis.edf_pdc",
    "drts_mp1.analysis.priority",
    "drts_mp1.analysis.math_utils",
    "drts_mp1.simulation.engine",
    "drts_mp1.simulation.state",
    "drts_mp1.simulation.event_queue",
    "drts_mp1.simulation.policies.base",
    "drts_mp1.simulation.policies.rm",
    "drts_mp1.simulation.policies.dm",
    "drts_mp1.simulation.policies.edf",
    "drts_mp1.metrics.response_times",
    "drts_mp1.metrics.preemptions",
    "drts_mp1.metrics.jitter",
    "drts_mp1.metrics.summarize",
    "drts_mp1.orchestration.run_one",
    "drts_mp1.orchestration.run_batch",
    "drts_mp1.orchestration.compare",
    "drts_mp1.orchestration.manifest",
    "drts_mp1.cli.main",
    "drts_mp1.cli.commands.analyze",
    "drts_mp1.cli.commands.simulate",
    "drts_mp1.cli.commands.run",
    "drts_mp1.cli.commands.batch",
]


def test_imports() -> None:
    for module_name in MODULES:
        importlib.import_module(module_name)
