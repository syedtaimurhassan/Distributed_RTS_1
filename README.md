# README
## Commands

Run these commands from the repository root.

1. `python3 -m drts_mp1.cli.main --help`  
   Show all available CLI commands.

2. `python3 -m drts_mp1.cli.main analyze --help`  
   Show options for analysis-only mode.

3. `python3 -m drts_mp1.cli.main simulate --help`  
   Show options for simulation-only mode.

4. `python3 -m drts_mp1.cli.main run --help`  
   Show options for full pipeline mode (analysis + simulation + compare).

5. `python3 -m drts_mp1.cli.main batch --help`  
   Show options for batch mode (recursive CSV processing).

6. `python3 -m drts_mp1.cli.main analyze task-set-example.csv --out results/runs`  
   Run DM/EDF analysis on one CSV and write a new run folder.

7. `python3 -m drts_mp1.cli.main simulate task-set-example.csv --policy rm --stop kH --k 1 --out results/runs`  
   Run RM simulation on one CSV (stop at `1 * hyperperiod`).

8. `python3 -m drts_mp1.cli.main simulate task-set-example.csv --policy dm --stop kH --k 1 --out results/runs`  
   Run DM simulation on one CSV.

9. `python3 -m drts_mp1.cli.main simulate task-set-example.csv --policy edf --stop kH --k 1 --out results/runs`  
   Run EDF simulation on one CSV.

10. `python3 -m drts_mp1.cli.main run task-set-example.csv --policies rm,dm,edf --stop kH --k 1 --out results/runs`  
    Run full pipeline: analyses + RM/DM/EDF simulations + comparison CSVs.

11. `python3 -m drts_mp1.cli.main batch output/automotive-utilDist/automotive-perDist/1-core/25-task/0-jitter/0.10-util/tasksets --policies dm,edf --stop kH --k 1 --out results/runs`  
    Run batch over the extracted dataset subfolder under `output` and write `batch_manifest.csv`.

12. `ls -td results/runs/* | head -n 1`  
    Print newest run folder path.

13. `find "$(ls -td results/runs/* | head -n 1)" -maxdepth 1 -type f | sort`  
    List files generated in the newest run.

14. `python3 -m unittest -q`  
    Run tests quickly.
