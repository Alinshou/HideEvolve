"""Program-level blind watermark evaluator and failure accounting."""

import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

import numpy as np
from PIL import Image
import yaml

from .attacks import apply_attack


ROOT = Path(__file__).resolve().parents[2]


def preprocess(path: Path, size: int = 256) -> np.ndarray:
    with Image.open(path) as opened:
        picture = opened.convert("RGB")
        width, height = picture.size
        side = min(width, height)
        left, top = (width-side)//2, (height-side)//2
        picture = picture.crop((left, top, left+side, top+side))
        return np.asarray(picture.resize((size, size), Image.Resampling.LANCZOS), dtype=np.uint8).copy()


def psnr(original: np.ndarray, changed: np.ndarray) -> float:
    mse = np.mean((original.astype(np.float64)-changed.astype(np.float64))**2)
    return float("inf") if mse == 0 else float(10 * np.log10(255**2 / mse))


def _call(candidate: Path, operation: str, image: np.ndarray, key: bytes,
          payload_bits: int, timeout: float, message: np.ndarray | None = None) -> np.ndarray:
    # The decode request has no message, original image, attack ID or attack parameters.
    request = {"operation": operation, "shape": list(image.shape),
               "image_b64": base64.b64encode(image.tobytes()).decode("ascii"),
               "key_hex": key.hex(), "payload_bits": payload_bits}
    if operation == "embed":
        request["message_bits"] = message.tolist()
    safe_env = {k: os.environ[k] for k in ["PATH", "SystemRoot", "WINDIR", "TEMP", "TMP"] if k in os.environ}
    safe_env.update(PYTHONUTF8="1", PYTHONNOUSERSITE="1", PYTHONPATH=str(ROOT / "src"))
    with tempfile.TemporaryDirectory(prefix="hideevolve-worker-") as workdir:
        completed = subprocess.run([sys.executable, "-m", "hideevolve.worker", str(candidate)],
                                   cwd=workdir, env=safe_env, input=json.dumps(request),
                                   text=True, capture_output=True, timeout=timeout)
    if len(completed.stdout) > 1048576 or len(completed.stderr) > 1048576:
        raise ValueError("child output exceeds cap")
    if not candidate.is_relative_to(ROOT):
        raise ValueError("candidate must be inside the project workspace")
    try:
        response = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError("candidate child returned malformed JSON") from error
    if completed.returncode:
        raise RuntimeError(f"{response.get('error_type','ChildError')}: {response.get('error','unknown')}")
    if operation == "decode":
        return np.asarray(response["bits"], dtype=np.uint8)
    return np.frombuffer(base64.b64decode(response["image_b64"]), dtype=np.uint8).reshape(image.shape).copy()


def evaluate(candidate: Path, image: np.ndarray, *, seed: int,
             protocol_path: Path = ROOT / "configs/protocol_v1.yaml") -> dict:
    protocol = yaml.safe_load(protocol_path.read_text(encoding="utf-8"))
    attacks = yaml.safe_load((ROOT / protocol["attacks_config"]).read_text(encoding="utf-8"))["attacks"]
    bits = int(protocol["payload_bits"])
    if image.shape != (256, 256, 3) or image.dtype != np.uint8:
        raise ValueError("evaluator image must be 256x256 RGB uint8")
    candidate = candidate.resolve(strict=True)
    source = candidate.read_bytes()
    result = {"candidate_sha256": hashlib.sha256(source).hexdigest(), "seed": seed,
              "protocol": protocol["schema_version"], "proposed": 1, "feasible": False,
              "score": 0.0, "status": "pending", "attacks": {}, "failure": None}
    started = time.monotonic()
    try:
        if len(source) > protocol["limits"]["max_candidate_source_bytes"]:
            raise ValueError("candidate source exceeds cap")
        rng = np.random.default_rng(seed)
        message = rng.integers(0, 2, size=bits, dtype=np.uint8)
        key = rng.bytes(int(protocol["key_bytes"]))
        watermarked = _call(candidate, "embed", image, key, bits,
                            protocol["limits"]["embed_timeout_seconds"], message)
        quality = psnr(image, watermarked)
        result["psnr_db"] = quality
        if quality < protocol["quality"]["minimum_psnr_db"]:
            raise ValueError("quality below PSNR threshold")
        for spec in attacks:
            attacked = apply_attack(watermarked, spec)
            decoded = _call(candidate, "decode", attacked, key, bits,
                            protocol["limits"]["decode_timeout_seconds"])
            if decoded.shape != (bits,):
                raise ValueError("wrong decoded payload length")
            errors = int(np.count_nonzero(decoded != message))
            result["attacks"][spec["id"]] = {"ber": errors / bits, "message_success": errors == 0}
            if spec["id"] == "A0_identity" and errors:
                raise ValueError("no-attack message recovery failed")
        if not result["attacks"]["A0_identity"]["message_success"]:
            raise ValueError("no-attack message recovery failed")
        result["feasible"] = True
        result["score"] = float(np.mean([v["message_success"] for v in result["attacks"].values()]))
        result["status"] = "completed_valid"
    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["failure"] = "candidate timeout"
    except (Exception, SystemExit) as error:
        result["status"] = "invalid"
        result["failure"] = f"{type(error).__name__}: {error}"[:400]
    result["wall_seconds"] = time.monotonic()-started
    return result
