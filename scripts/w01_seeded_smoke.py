"""Run a bounded official example with explicit host RNG state and budget reservation."""

import argparse
import csv
from datetime import datetime
import json
import os
from pathlib import Path
import random
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / "tmp/w01-install-repro-20261009/Scripts/python.exe"
RESERVATIONS = ROOT / "experiments/w01_budget_reservations.csv"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", choices=["c", "d"], required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--child", action="store_true")
    args = parser.parse_args()
    if args.child:
        import numpy as np
        random.seed(args.seed)
        np.random.seed(args.seed)
        from shinka.cli.launch import main as official_main
        result = ROOT / f"experiments/runs/w01-shinka-seeded-{args.run}"
        official_main([
            "variant=circle_packing_example", f"results_dir={result.as_posix()}",
            f"run_name=run-{args.run}", "max_evaluation_jobs=1", "max_proposal_jobs=1",
            "max_db_workers=1", "db_config.num_islands=1", "evo_config.llm_models=[deepseek-chat]",
            "evo_config.llm_dynamic_selection=null", "evo_config.embedding_model=null",
            "evo_config.num_generations=2", "+evo_config.max_api_costs=0.05",
            "evo_config.max_patch_attempts=1", "evo_config.max_patch_resamples=1",
            "evo_config.llm_kwargs.temperatures=[0]", "evo_config.llm_kwargs.max_tokens=4096",
            "evo_config.meta_rec_interval=null", "evo_config.meta_llm_models=[]"])
        return

    import yaml
    from dotenv import dotenv_values
    result = ROOT / f"experiments/runs/w01-shinka-seeded-{args.run}"
    if result.exists():
        raise SystemExit("Refusing to overwrite an existing run.")
    budget = yaml.safe_load((ROOT / "configs/budget_v0.yaml").read_text(encoding="utf-8"))
    with (ROOT / "experiments/cost_probe.csv").open(encoding="utf-8", newline="") as f:
        prior = sum(float(r["cost_cny"] or 0) for r in csv.DictReader(f))
    reserved = 0.0
    if RESERVATIONS.exists():
        with RESERVATIONS.open(encoding="utf-8", newline="") as f:
            reserved = sum(float(r["reserved_cny"]) for r in csv.DictReader(f))
    # Reserve the full USD 0.05 upstream stop value, well above one anticipated proposal.
    cap = 0.36
    if prior + reserved + cap > min(budget["total_hard_cap"], budget["phase_caps"]["W01_W04_baseline_and_bottleneck"]):
        raise SystemExit("Phase or total policy budget exhausted.")
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        key = dotenv_values(ROOT.parent / "Foundation Model Agent/.env").get("DEEPSEEK_API_KEY")
    if not key:
        raise SystemExit("DEEPSEEK_API_KEY is required locally; no request was made.")
    new = not RESERVATIONS.exists()
    with RESERVATIONS.open("a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if new: writer.writerow(["run_id", "reserved_at", "host_seed", "reserved_cny", "notes"])
        writer.writerow([f"w01-shinka-seeded-{args.run}-001", datetime.now().astimezone().isoformat(),
                         args.seed, cap, "One generated proposal; output cap 4096; no embedding/meta calls; pre-run reservation, not billing"])
    result.mkdir(parents=True)
    env = os.environ.copy()
    env.update(DEEPSEEK_API_KEY=key, PYTHONHASHSEED=str(args.seed), PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    started = datetime.now().astimezone()
    command = [str(PYTHON), str(Path(__file__).resolve()), "--run", args.run, "--seed", str(args.seed), "--child"]
    with (result / "launch_stdout.log").open("x", encoding="utf-8") as log:
        code = subprocess.call(command, cwd=ROOT / "third_party/ShinkaEvolve", env=env, stdout=log, stderr=log)
    finished = datetime.now().astimezone()
    metadata = {"run_id": f"w01-shinka-seeded-{args.run}-001", "host_seed": args.seed,
                "rng_policy": "PYTHONHASHSEED, random.seed, numpy.random.seed before official launcher",
                "model_seed": None, "model_seed_note": "DeepSeek request has no API seed; temperature=0 does not guarantee identical responses",
                "started_at": started.isoformat(), "finished_at": finished.isoformat(),
                "wall_seconds": (finished-started).total_seconds(), "exit_code": code,
                "reservation_cny": cap, "python": str(PYTHON), "output_token_cap": 4096}
    (result / "host_run.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    if code: raise SystemExit(code)


if __name__ == "__main__":
    main()
