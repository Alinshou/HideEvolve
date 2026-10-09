"""Collect new seeded W01 runs and verify a portable evidence bundle."""

import csv
from datetime import datetime
import hashlib
import json
import io
from pathlib import Path
import re
import shutil
import sqlite3
import zipfile

from w01_archive_evidence import ROOT, save_json, render_log


def write_csv(path, rows):
    if path.exists():
        with path.open(encoding="utf-8", newline="") as f:
            existing = list(csv.DictReader(f))
        expected = [{k: str(v) for k, v in r.items()} for r in rows]
        if existing != expected:
            raise RuntimeError("Existing ledger differs; refusing replacement")
        return
    with path.open("x", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    out = ROOT / "repro/w01_closeout_evidence"
    if out.exists():
        raise SystemExit("Refusing to overwrite existing closeout evidence.")
    out.mkdir()
    costs, runs = [], []
    for label in ["c", "d"]:
        parent = ROOT / f"experiments/runs/w01-shinka-seeded-{label}"
        original = parent / f"shinka_circle_packing/run-{label}_example"
        host = json.loads((parent / "host_run.json").read_text(encoding="utf-8"))
        if host["exit_code"] != 0:
            raise RuntimeError("Official run did not exit successfully")
        dest = out / f"run_{label}"
        dest.mkdir()
        for rel in ["gen_0/main.py", "gen_0/results/metrics.json", "gen_0/results/correct.json",
                    "gen_1/main.py", "gen_1/results/metrics.json", "gen_1/results/correct.json",
                    "gen_1/results/extra.npz", "gen_1/results/job_log.out", "gen_1/results/job_log.err",
                    ".hydra/config.yaml", ".hydra/overrides.yaml", "launch_hydra.log", "evolution_run.log"]:
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(original / rel, target)
        shutil.copy2(parent / "host_run.json", dest / "host_run.json")
        shutil.copy2(parent / "launch_stdout.log", dest / "launch_stdout.log")
        source = sqlite3.connect("file:" + (original / "programs.sqlite").as_posix() + "?mode=ro", uri=True)
        backup = sqlite3.connect(dest / "programs.sqlite")
        source.backup(backup)
        if backup.execute("pragma integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("SQLite integrity check failed")
        backup.close()
        meta = json.loads(source.execute("select metadata from programs where generation=1").fetchone()[0])
        source.close()
        llm = meta["llm_result"]
        if llm["num_total_queries"] != 1:
            raise RuntimeError("Unexpected model query count")
        prompt = dest / "stored_prompt.json"
        save_json(prompt, {"system_msg": llm["system_msg"], "msg": llm["msg"]})
        prompt_hash = hashlib.sha256(prompt.read_bytes()).hexdigest()
        correct = json.loads((dest / "gen_1/results/correct.json").read_text())
        metrics = json.loads((dest / "gen_1/results/metrics.json").read_text())
        cost_cny = llm["cost"] * 7.2
        if cost_cny > host["reservation_cny"]:
            raise RuntimeError("Run exceeded pre-run reservation")
        costs.append({"run_id": host["run_id"], "timestamp": host["started_at"],
                      "provider": "DeepSeek", "model": llm["model_name"], "prompt_sha256": prompt_hash,
                      "input_tokens": llm["input_tokens"], "output_tokens": llm["output_tokens"],
                      "queries": llm["num_total_queries"], "framework_cost_usd": llm["cost"],
                      "estimated_cost_cny": cost_cny, "billed_cost_cny": "", "wall_seconds": host["wall_seconds"],
                      "sampling_seconds": meta["sampling_seconds"], "evaluation_seconds": meta["evaluation_seconds"],
                      "execution_seconds": metrics["execution_time_mean"],
                      "status": "completed_valid" if correct["correct"] else "completed_invalid",
                      "notes": "Prompt hash is archived stored JSON bytes; cost uses planning exchange rate 7.2, not invoice"})
        runs.append({"run_id": host["run_id"], "host_seed": host["host_seed"], "model_api_seed": None,
                     "upstream_commit": "8adc053a2ce4511ad2ac310e004c530a73fb974a",
                     "python": host["python"], "output_token_cap": host["output_token_cap"],
                     "candidate_cap": 1, "exit_code": host["exit_code"], "correct": correct["correct"],
                     "raw_score": metrics["combined_score"], "error": correct["error"],
                     "candidate_sha256": hashlib.sha256((dest / "gen_1/main.py").read_bytes()).hexdigest(),
                     "prompt_sha256": prompt_hash})
        save_json(dest / "verified_metadata.json", {"run": runs[-1], "cost": costs[-1], "host": host})
        render_log(dest / "launch_hydra.log", dest / "log_display.png", label.upper())
    write_csv(ROOT / "experiments/w01_closeout_costs.csv", costs)
    save_json(ROOT / "repro/w01_closeout_summary.json", {
        "collected_at": datetime.now().astimezone().isoformat(),
        "install_reproduction": "repro/install.log",
        "runs": runs, "costs": costs,
        "engineering_gate": "GO",
        "limits": "No watermark performance claim. API sampling remains nondeterministic. Costs are estimates."})
    for rel in ["repro/install.log", "repro/repo_audit.md", "repro/hardware.yaml", "repro/env-lock.md",
                "repro/requirements-lock.txt", "docs/REEVO_INTEGRATION_RISK_W01.md",
                "experiments/w01_closeout_costs.csv", "experiments/w01_budget_reservations.csv",
                "experiments/cost_probe.csv", "experiments/run_manifest.csv", "configs/budget_v0.yaml",
                "repro/w01_closeout_summary.json", "scripts/w01_install_repro.py", "scripts/w01_seeded_smoke.py",
                "scripts/w01_archive_evidence.py", "scripts/w01_collect_closeout.py"]:
        dest = out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dest)
    shutil.copy2(ROOT / "tmp/w01-evidence-20261009.zip", out / "original_smoke_evidence.zip")
    save_json(out / "README.json", {
        "created_at": datetime.now().astimezone().isoformat(),
        "original_install_log": "Missing; install.log is a separately dated clean-environment reproduction",
        "new_runs": "C/D run the unchanged official example in the newly installed environment",
        "old_runs": "Nested original_smoke_evidence.zip preserves A2/B; contains its own checksum file",
        "log_images": "Post-run renderings; exact text logs and source line numbers accompany them",
        "seeds": "Host Python/hash/NumPy RNG seeds recorded. No DeepSeek API seed is promised.",
        "prompts": "Hashes refer to exact archived stored_prompt.json files, not network requests",
        "costs": "Framework-estimated USD and planning CNY. Provider invoices are not reconciled."})
    files = sorted(p for p in out.rglob("*") if p.is_file())
    for p in files:
        if p.suffix not in [".zip", ".png", ".npz"]:
            raw = p.read_bytes()
            if re.search(rb"sk-[A-Za-z0-9]{20,}|Authorization: Bearer [A-Za-z0-9._-]{20,}", raw):
                raise RuntimeError(f"Possible secret token in {p.name}; evidence bundle not approved")
    checksum = out / "SHA256SUMS.txt"
    checksum.write_text("".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(out).as_posix()}\n" for p in files), encoding="utf-8")
    archive = ROOT / "每周实验报告/W01_完整证据包_20261009.zip"
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED) as z:
        for p in out.rglob("*"):
            if p.is_file(): z.write(p, p.relative_to(out))
    with zipfile.ZipFile(archive) as z:
        if z.testzip(): raise RuntimeError("ZIP CRC failed")
        for line in checksum.read_text(encoding="utf-8").splitlines():
            expected, name = line.split("  ", 1)
            if hashlib.sha256(z.read(name)).hexdigest() != expected:
                raise RuntimeError("Archive readback mismatch: " + name)
    save_json(ROOT / "repro/w01_archive_receipt.json", {
        "archive": archive.relative_to(ROOT).as_posix(), "bytes": archive.stat().st_size,
        "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "file_count_excluding_checksum": len(files), "zip_crc": "PASS", "all_hash_readback": "PASS",
        "sqlite_integrity": "PASS", "checked_at": datetime.now().astimezone().isoformat()})
    print(json.dumps({"runs": runs, "costs": costs}, ensure_ascii=False, indent=2))
    print("PASS: evidence ZIP, SQLite and hash readback verified")


if __name__ == "__main__":
    main()
