"""Run local, unpaid W02 evaluator smoke tests on frozen D-search images."""

import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hideevolve.runner import evaluate, preprocess


def main():
    output = ROOT / "experiments/w02_smoke_20261009.json"
    if output.exists():
        raise SystemExit("Refusing to overwrite smoke evidence")
    manifest = ROOT / "data/splits_d_search_v1.sha256"
    entries = [line.split("  ", 1) for line in manifest.read_text(encoding="utf-8").splitlines()[:3]]
    source = ROOT.parent / "Foundation Model Agent/data/raw/coco/val2017"
    results = []
    for expected_hash, name in entries:
        path = source / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
            raise RuntimeError("Image hash mismatch")
        image = preprocess(path)
        for baseline in ["spatial_lsb", "dct_qim"]:
            candidate = ROOT / f"src/hideevolve/baselines/{baseline}.py"
            result = evaluate(candidate, image, seed=2026100901 + len(results))
            results.append({"image": name, "baseline": baseline, **result})
            print(name, baseline, result["status"], result["psnr_db"] if "psnr_db" in result else "", result["failure"])
    output.write_text(json.dumps({"date": "2026-10-09", "phase": "W02 exploratory",
                                  "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
                                  "results": results}, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    if not all(r["feasible"] for r in results):
        raise SystemExit("At least one smoke baseline failed")


if __name__ == "__main__":
    main()
