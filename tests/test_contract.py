"""W02 scientific contract and failure-accounting checks."""

import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hideevolve.attacks import apply_attack
from hideevolve.runner import _call, evaluate


class W02Contract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image = np.random.default_rng(502).integers(0, 256, size=(256, 256, 3), dtype=np.uint8)
        cls.baselines = ROOT / "src/hideevolve/baselines"
        cls.fixtures = ROOT / "tests/fixtures"

    def test_two_mathematical_structures_share_evaluator(self):
        for name in ["spatial_lsb.py", "dct_qim.py"]:
            with self.subTest(name=name):
                result = evaluate(self.baselines / name, self.image, seed=502)
                self.assertEqual(result["status"], "completed_valid", result["failure"])
                self.assertEqual(result["attacks"]["A0_identity"]["ber"], 0.0)
                self.assertGreaterEqual(result["psnr_db"], 35.0)

    def test_decode_child_request_has_no_original_message_or_attack_truth(self):
        requests = []

        def intercept(*args, **kwargs):
            requests.append(json.loads(kwargs["input"]))
            return subprocess.CompletedProcess(args, 0, stdout=json.dumps({"bits": [0] * 32}), stderr="")

        with patch("hideevolve.runner.subprocess.run", side_effect=intercept):
            _call(self.baselines / "spatial_lsb.py", "decode", self.image, b"k" * 16, 32, 1)
        self.assertEqual(len(requests), 1)
        self.assertEqual(set(requests[0]), {"operation", "shape", "image_b64", "key_hex", "payload_bits"})
        self.assertNotIn("DEEPSEEK_API_KEY", requests[0])

    def test_blind_message_lookup_fails(self):
        result = evaluate(self.fixtures / "bad_message.py", self.image, seed=502)
        self.assertFalse(result["feasible"])
        self.assertEqual(result["proposed"], 1)

    def test_candidate_cannot_open_original_image_from_local_filesystem(self):
        result = evaluate(self.fixtures / "bad_leak.py", self.image, seed=502)
        self.assertFalse(result["feasible"])
        self.assertIn("filesystem access blocked", result["failure"])

    def test_timeout_exception_and_quality_each_consume_slot(self):
        for fixture, status in [("bad_timeout.py", "timeout"),
                                ("bad_exception.py", "invalid"),
                                ("bad_quality.py", "invalid")]:
            with self.subTest(fixture=fixture):
                result = evaluate(self.fixtures / fixture, self.image, seed=502)
                self.assertEqual(result["proposed"], 1)
                self.assertEqual(result["status"], status)
                self.assertFalse(result["feasible"])
                self.assertEqual(result["score"], 0.0)

    def test_attacks_are_deterministic_and_keep_shape(self):
        attack_specs = yaml.safe_load((ROOT / "configs/attacks_v0.yaml").read_text(encoding="utf-8"))["attacks"]
        for spec in attack_specs:
            with self.subTest(attack=spec["id"]):
                a = apply_attack(self.image, spec)
                b = apply_attack(self.image, spec)
                self.assertEqual(a.shape, self.image.shape)
                self.assertEqual(a.dtype, np.uint8)
                self.assertTrue(np.array_equal(a, b))

    def test_frozen_split_identity_and_hashes(self):
        source = ROOT.parent / "Foundation Model Agent/data/raw/coco/val2017"
        sets = {}
        for name, expected in [("d_search", 60), ("d_select", 20), ("d_test", 1000)]:
            path = ROOT / f"data/splits_{name}_v1.sha256"
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), expected)
            rows = [line.split("  ", 1) for line in lines]
            sets[name] = {filename for _, filename in rows}
            self.assertEqual(len(sets[name]), expected)
            # Verify a selected development image. D-test pixels remain unevaluated.
            if name != "d_test":
                hash_value, filename = rows[0]
                self.assertEqual(hashlib.sha256((source / filename).read_bytes()).hexdigest(), hash_value)
        self.assertFalse(sets["d_search"] & sets["d_select"])
        self.assertFalse(sets["d_search"] & sets["d_test"])
        self.assertFalse(sets["d_select"] & sets["d_test"])
        excluded = {line.split("  ", 1)[1] for line in (ROOT / "data/historical_excluded_v1.sha256").read_text().splitlines()}
        self.assertEqual(len(excluded), 1100)
        self.assertFalse((sets["d_search"] | sets["d_select"] | sets["d_test"]) & excluded)
        receipt = json.loads((ROOT / "data/splits_v1_receipt.json").read_text(encoding="utf-8"))
        for name in sets:
            path = ROOT / f"data/splits_{name}_v1.sha256"
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), receipt["splits"][name]["manifest_sha256"])


if __name__ == "__main__":
    unittest.main()
