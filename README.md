# README
## Setup (venv + dependencies)
Run setup once from repository root:

1. `bash make.sh`  
   Creates `.venv`, upgrades `pip`, and installs `requirements.txt`.

2. `source .venv/bin/activate`  
   Activates the virtual environment.

3. `python3 -m drts_mp1.cli.main --help`  
   Verifies CLI is available.

## CLI Commands
Run all commands from repository root.

1. `python3 -m drts_mp1.cli.main --help`  
   Show all available commands.

2. `python3 -m drts_mp1.cli.main analyze --help`  
   Show analysis command options.

3. `python3 -m drts_mp1.cli.main simulate --help`  
   Show simulation command options.

4. `python3 -m drts_mp1.cli.main run --help`  
   Show full pipeline command options.

5. `python3 -m drts_mp1.cli.main batch --help`  
   Show batch command options.

## Full Command Forms
These are the complete command entrypoints currently implemented:

1. `python3 -m drts_mp1.cli.main analyze <taskset_csv> --out <out_dir> --execution-mode single|multi --cores <int>`
2. `python3 -m drts_mp1.cli.main simulate <taskset_csv> --policy rm|dm|edf --stop H|kH --k <int> --out <out_dir> --execution-mode single|multi --cores <int> --exec-time wcet|uniform --seed <int>`
3. `python3 -m drts_mp1.cli.main run <taskset_csv> --policies rm,dm,edf --stop H|kH --k <int> --out <out_dir> --execution-mode single|multi --cores <int> --exec-time wcet|uniform --seed <int>`
4. `python3 -m drts_mp1.cli.main batch <input_dir> --policies rm,dm,edf --stop H|kH --k <int> --out <out_dir> --execution-mode single|multi --cores <int> --exec-time wcet|uniform --seed <int>`

## Execution Modes
Use `--execution-mode` and `--cores` on `analyze`, `simulate`, `run`, and `batch`.

- `--execution-mode single`  
  Single-core mode. All tasks run on one core. `PE` is kept as metadata and ignored for scheduling.

- `--execution-mode multi`  
  Multi-core mode. Tasks are partitioned by `PE` and each partition is simulated independently.

- `--cores N`  
  Number of configured cores.  
  In `single`, use `--cores 1`.  
  In `multi`, `PE` values must map to configured cores (`0..N-1` or `1..N`).

## Common Runs
1. `python3 -m drts_mp1.cli.main analyze task-set-example.csv --out results/runs --execution-mode single --cores 1`  
   Analysis-only run on one CSV, explicit single-core.

2. `python3 -m drts_mp1.cli.main simulate task-set-example.csv --policy rm --stop kH --k 1 --out results/runs --execution-mode single --cores 1`  
   RM simulation on one CSV in single-core mode.

3. `python3 -m drts_mp1.cli.main run task-set-example.csv --policies rm,dm,edf --stop kH --k 1 --out results/runs --execution-mode single --cores 1`  
   Full pipeline (analysis + simulation + compare) for one CSV in single-core mode.

4. `python3 -m drts_mp1.cli.main run task-set-example.csv --policies rm,dm,edf --stop kH --k 1 --out results/runs --execution-mode multi --cores 2`  
   Full pipeline for one CSV in multi-core mode (partition by `PE`).

5. `python3 -m drts_mp1.cli.main batch output --policies rm,dm,edf --stop kH --k 1 --out results/runs_single_full --execution-mode single --cores 1`  
   Batch all provided task sets under `output` in single-core mode.

6. `python3 -m drts_mp1.cli.main batch output --policies rm,dm,edf --stop kH --k 1 --out results/runs_multi_full --execution-mode multi --cores 4`  
   Batch all provided task sets under `output` in multi-core mode.

## Logs and Output Inspection
Folder layout now uses per-invocation run groups:

`results/runs/<execution-mode>-<cores>c-<timestamp>/<run_id>/...`

For batch runs, the same group folder also contains:
- `batch_manifest.csv`
- `batch_log.txt`

1. `ls -td results/runs*/* | head -n 1`  
   Print newest run folder.

2. `find "$(ls -td results/runs*/* | head -n 1)" -maxdepth 1 -type f | sort`  
   List files generated in newest run.

3. `cat "$(ls -td results/runs*/* | head -n 1)/run_metadata.csv"`  
   Show run metadata including `execution_mode`, `core_count`, and `active_cores`.

4. `sed -n '1,80p' "$(ls -td results/runs*/* | head -n 1)/run_log.txt"`  
   Show per-run execution log (core mapping and per-policy/core stats).

5. `cat results/runs_single_full/batch_manifest.csv | head -n 5`  
   Show batch manifest with mode/core columns.

6. `sed -n '1,80p' results/runs_single_full/batch_log.txt`  
   Show batch-level log.

7. `python3 -m unittest -q`  
   Run tests.
