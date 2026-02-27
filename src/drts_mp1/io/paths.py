"""Path helpers for creating run folders and storing run artifacts."""

from __future__ import annotations

import hashlib
import shutil
from datetime import datetime, timezone
from pathlib import Path


def create_run_id(taskset_path: str | Path) -> str:
    """Create run ID using UTC timestamp and a short deterministic-ish hash."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    digest_input = f"{Path(taskset_path).resolve()}-{ts}".encode("utf-8")
    short_hash = hashlib.sha1(digest_input).hexdigest()[:8]
    return f"{ts}-{short_hash}"


def create_run_folder(out_root: str | Path, run_id: str) -> Path:
    """Create `results/runs/<run_id>` (or custom root) and return the path."""
    root = Path(out_root)
    run_dir = root / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def copy_input_taskset(taskset_path: str | Path, run_dir: str | Path) -> Path:
    """Copy the exact input CSV into the run folder as `input_taskset.csv`."""
    src = Path(taskset_path)
    dst = Path(run_dir) / "input_taskset.csv"
    shutil.copyfile(src, dst)
    return dst
