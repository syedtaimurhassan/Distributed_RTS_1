"""Path helpers for creating run folders and storing run artifacts."""

from __future__ import annotations

import hashlib
import shutil
from datetime import datetime, timezone
from pathlib import Path


def create_run_group_id(execution_mode: str, core_count: int) -> str:
    """Create group ID for one command invocation.

    Format:
    - <mode>-<cores>c-<timestamp>
    Example:
    - single-1c-20260306T101530123456Z
    """
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    mode = execution_mode.strip().lower()
    return f"{mode}-{core_count}c-{ts}"


def create_run_group_folder(
    out_root: str | Path,
    execution_mode: str,
    core_count: int,
) -> Path:
    """Create a per-invocation run-group directory and return its path."""
    root = Path(out_root)
    group_dir = root / create_run_group_id(
        execution_mode=execution_mode,
        core_count=core_count,
    )
    group_dir.mkdir(parents=True, exist_ok=False)
    return group_dir


def create_run_id(taskset_path: str | Path) -> str:
    """Create run ID using UTC timestamp and a short deterministic-ish hash."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    digest_input = f"{Path(taskset_path).resolve()}-{ts}".encode("utf-8")
    short_hash = hashlib.sha1(digest_input).hexdigest()[:8]
    return f"{ts}-{short_hash}"


def create_run_folder(out_root: str | Path, run_id: str) -> Path:
    """Create `<out_root>/<run_id>` and return the path."""
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
