"""Export the existing W01 evidence without modifying original runs."""

import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import textwrap
import zipfile

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "repro" / "w01_evidence"


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render_log(source, target, label):
    lines = source.read_text(encoding="utf-8").splitlines()
    excerpt = [(i + 1, line) for i, line in enumerate(lines)
               if any(s in line for s in ["ASYNC EVOLUTION RUN STARTED", "Max API costs",
                                          "VALID RESULTS:", "JOB COMPLETE:", "Async database closed"])]
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 21)
    small = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 17)
    rows = [f"{n}: {line}" for n, line in excerpt]
    wrapped = [part for row in rows for part in textwrap.wrap(row, 102)]
    im = Image.new("RGB", (1500, 190 + 33 * len(wrapped)), "#f5f7fa")
    draw = ImageDraw.Draw(im)
    draw.text((30, 22), f"W01 {label} 原始日志展示图", font=font, fill="#172b4d")
    draw.text((30, 60), "生成方式：已有文本日志的事后渲染；不是运行当时的桌面截图。", font=small, fill="#394b63")
    draw.text((30, 89), "左侧为原文件行号；未改写日志内容。完整原始日志随证据包提供。", font=small, fill="#394b63")
    y = 140
    for row in wrapped:
        draw.text((30, y), row, font=small, fill="#101828")
        y += 33
    im.save(target)


def main():
    if OUT.exists():
        raise SystemExit("Refusing to overwrite an existing evidence archive.")
    OUT.mkdir()
    records = []
    for label in ["a2", "b"]:
        original = ROOT / f"experiments/runs/w01-shinka-deepseek-{label}/shinka_circle_packing/run-{label}_example"
        dest = OUT / f"run_{label}"
        dest.mkdir()
        for rel in ["gen_0/main.py", "gen_0/results/metrics.json", "gen_0/results/correct.json",
                    "gen_1/main.py", "gen_1/results/metrics.json", "gen_1/results/correct.json",
                    "gen_1/results/extra.npz", "gen_1/results/job_log.out", "gen_1/results/job_log.err",
                    ".hydra/config.yaml", ".hydra/overrides.yaml", "launch_hydra.log", "evolution_run.log"]:
            p = dest / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(original / rel, p)
        source = sqlite3.connect("file:" + (original / "programs.sqlite").as_posix() + "?mode=ro", uri=True)
        backup = sqlite3.connect(dest / "programs.sqlite")
        source.backup(backup)
        if backup.execute("pragma integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("SQLite backup integrity check failed")
        backup.close()
        meta = json.loads(source.execute("select metadata from programs where generation=1").fetchone()[0])
        llm = meta["llm_result"]
        prompt = dest / "stored_prompt.json"
        save_json(prompt, {"system_msg": llm["system_msg"], "msg": llm["msg"]})
        # Hash the exact archived UTF-8 JSON bytes, not a reconstructed API wire request.
        digest = hashlib.sha256(prompt.read_bytes()).hexdigest()
        records.append({"run_id": f"w01-shinka-{label}-001", "stored_prompt_sha256": digest,
                        "stored_prompt_path": prompt.relative_to(ROOT).as_posix(),
                        "definition": "SHA256 of archived stored_prompt.json bytes; stored system_msg and msg"})
        save_json(dest / "verified_metadata.json", {
            "model": llm["model_name"], "input_tokens": llm["input_tokens"],
            "output_tokens": llm["output_tokens"], "framework_cost_usd": llm["cost"],
            "num_total_queries": llm["num_total_queries"],
            **{k: meta[k] for k in ["sampling_seconds", "evaluation_seconds", "pipeline_seconds"]},
            "framework_seed": None, "framework_seed_note": "Not frozen in the original smoke runs"})
        source.close()
        render_log(dest / "launch_hydra.log", dest / "log_display.png", label.upper())
    failed = ROOT / "experiments/runs/w01-shinka-deepseek-a/shinka_circle_packing/run-a_example/gen_1/failure.json"
    shutil.copy2(failed, OUT / "failed_before_model_call.json")
    for label in ["a", "b"]:
        dest = OUT / f"official_evaluator_{label}"
        dest.mkdir()
        original = ROOT / f"experiments/runs/w01-official-evaluator-{label}"
        for name in ["metrics.json", "correct.json"]:
            shutil.copy2(original / name, dest / name)
    with (OUT / "prompt_hash_corrections.csv").open("x", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)
    save_json(OUT / "archive_note.json", {
        "created_at": datetime.now().astimezone().isoformat(),
        "purpose": "Retrospective export of existing W01 engineering evidence",
        "original_runs_preserved": True,
        "sqlite_method": "SQLite online backup from read-only source; integrity_check=ok",
        "prompt_hash_method": "SHA256 of archived stored_prompt.json UTF-8 bytes",
        "log_images": "Retrospective renderings of exact log excerpts with original line numbers; not live desktop screenshots",
        "seed_limitation": "Original framework seeds were not frozen; no seeds were invented"})
    files = sorted(p for p in OUT.rglob("*") if p.is_file())
    for p in files:
        content = p.read_bytes()
        if b"sk-" in content or b"Authorization: Bearer " in content:
            raise RuntimeError(f"Possible secret marker in {p.name}; archive not approved")
    checksum = OUT / "SHA256SUMS.txt"
    checksum.write_text("".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(OUT).as_posix()}\n" for p in files), encoding="utf-8")
    archive = ROOT / "tmp" / "w01-evidence-20261009.zip"
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED) as z:
        for p in OUT.rglob("*"):
            if p.is_file(): z.write(p, p.relative_to(OUT))
    # Restore every archived file to memory and validate against the independent checksum listing.
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for line in checksum.read_text(encoding="utf-8").splitlines():
            expected, name = line.split("  ", 1)
            assert hashlib.sha256(z.read(name)).hexdigest() == expected, name
    print(f"PASS: {len(files)} evidence files; SQLite backups and ZIP readback hashes verified")
    print("ZIP SHA256:", hashlib.sha256(archive.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
