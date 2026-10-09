"""Freeze disjoint COCO identities for W02 without running any watermark model."""

import csv
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT.parent / "Foundation Model Agent"
RAW = OLD / "data/raw/coco/val2017"
OLD_100 = OLD / "data/manifests/coco_val2017_poc_v0.1.csv"
OLD_1000 = OLD / "旧版支线/stage7-development-identity-manifest-v01-20261003-01/development_manifest.jsonl"
OUT = ROOT / "data"


def digest_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def dhash(path):
    with Image.open(path) as opened:
        gray = opened.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
        pixels = list(gray.getdata())
    value = 0
    for row in range(8):
        for col in range(8):
            value = (value << 1) | int(pixels[row * 9 + col] > pixels[row * 9 + col + 1])
    return value


def main():
    with OLD_100.open(encoding="utf-8", newline="") as file:
        old_rows = list(csv.DictReader(file))
    prior = {r["relative_path"] for r in old_rows}
    old1000 = [json.loads(line) for line in OLD_1000.read_text(encoding="utf-8").splitlines()]
    if len(old1000) != 1000:
        raise RuntimeError("Historical development manifest is not 1000 rows")
    prior.update(r["relative_path"] for r in old1000)
    files = sorted(RAW.glob("*.jpg"))
    if len(files) != 5000 or len(prior) < 1000:
        raise RuntimeError("Unexpected local dataset inventory")
    existing = {p.name for p in files}
    if not prior <= existing:
        raise RuntimeError("Historical excluded files are missing locally")
    original_hashes = {r["relative_path"]: r["sha256"] for r in old_rows}
    original_hashes.update({r["relative_path"]: r["raw_sha256"] for r in old1000})
    for name in prior:
        if digest_file(RAW / name) != original_hashes[name]:
            raise RuntimeError("Historical image hash mismatch: " + name)
    prior_dhashes = [dhash(RAW / name) for name in sorted(prior)]
    # Deterministic pseudorandom priority, independent of filesystem traversal order.
    candidates = [p for p in files if p.name not in prior]
    candidates.sort(key=lambda p: hashlib.sha256(("HideEvolve-W02-v1:" + p.name).encode()).digest())
    selected = []
    seen_dhashes = list(prior_dhashes)
    rejected_near = 0
    for file in candidates:
        view_hash = dhash(file)
        if any((view_hash ^ previous).bit_count() <= 5 for previous in seen_dhashes):
            rejected_near += 1
            continue
        selected.append((file, view_hash))
        seen_dhashes.append(view_hash)
        if len(selected) == 1080:  # search 60, select 20, sealed test pool 1000
            break
    if len(selected) != 1080:
        raise RuntimeError("Not enough non-near-duplicate images for frozen splits")
    OUT.mkdir(exist_ok=True)
    plans = {"d_search": selected[:60], "d_select": selected[60:80], "d_test": selected[80:]}
    for split, rows in plans.items():
        target = OUT / f"splits_{split}_v1.sha256"
        if target.exists():
            raise RuntimeError("Refusing to overwrite frozen split: " + str(target))
        target.write_text("".join(f"{digest_file(p)}  {p.name}\n" for p, _ in rows), encoding="utf-8")
    excluded = OUT / "historical_excluded_v1.sha256"
    if excluded.exists():
        raise RuntimeError("Refusing to overwrite historical exclusion list")
    excluded.write_text("".join(f"{original_hashes[name]}  {name}\n" for name in sorted(prior)), encoding="utf-8")
    summary = {"captured_at": "2026-10-09", "source": "COCO 2017 val2017, local old project",
               "old_100_csv_sha256": digest_file(OLD_100),
               "old_1000_jsonl_sha256": digest_file(OLD_1000),
               "source_archive_sha256_recorded": "4f7e2ccb2866ec5041993c9cf2a952bbed69647b115d0f74da7ce8f4bef82f05",
               "historical_excluded_count": len(prior), "near_duplicate_metric": "64-bit grayscale dHash",
               "near_duplicate_reject_threshold": 5, "candidate_near_duplicates_rejected": rejected_near,
               "selection_domain": "HideEvolve-W02-v1:<12-digit file name> SHA-256 ascending",
               "test_access_policy": "D-test image bytes were opened only to compute source hashes and perceptual dHash during split construction; no watermark candidate or attack was evaluated on D-test. Formal evaluation remains sealed until W15.",
               "splits": {name: {"count": len(rows), "manifest_sha256": digest_file(OUT / f"splits_{name}_v1.sha256")}
                          for name, rows in plans.items()},
               "historical_excluded_manifest_sha256": digest_file(excluded)}
    (OUT / "splits_v1_receipt.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
