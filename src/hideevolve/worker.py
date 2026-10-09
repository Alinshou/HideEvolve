"""Single-use child process receiving only the inputs needed by one candidate call."""

import base64
import importlib.util
import json
import os
import sys

import numpy as np
import scipy.fft  # Load baseline math dependencies before candidate audit restrictions.


def _restrict_candidate_file_access(candidate_path):
    allowed_source = os.path.normcase(os.path.abspath(candidate_path))
    allowed_runtime = os.path.normcase(os.path.abspath(sys.prefix))
    allowed_stdlib = os.path.normcase(os.path.abspath(os.__file__))
    allowed_stdlib = os.path.dirname(allowed_stdlib)

    def audit(event, args):
        if event in {"subprocess.Popen", "os.system", "socket.connect", "socket.bind",
                     "ctypes.dlopen", "ctypes.dlsym", "os.listdir", "os.scandir", "os.chdir"}:
            raise PermissionError(f"candidate operation blocked: {event}")
        if event == "open":
            path = args[0]
            if isinstance(path, int):
                raise PermissionError("candidate file descriptor access blocked")
            if isinstance(path, (str, bytes, os.PathLike)):
                name = os.path.normcase(os.path.abspath(os.fsdecode(path)))
                allowed_package = name.startswith(allowed_runtime + os.sep) or name.startswith(allowed_stdlib + os.sep)
                if name != allowed_source and not allowed_package:
                    raise PermissionError("candidate filesystem access blocked")

    sys.addaudithook(audit)


def _load_candidate(path):
    spec = importlib.util.spec_from_file_location("hideevolve_candidate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("candidate module cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    request = json.load(sys.stdin)
    shape = tuple(request["shape"])
    image = np.frombuffer(base64.b64decode(request["image_b64"]), dtype=np.uint8).reshape(shape).copy()
    key = bytes.fromhex(request["key_hex"])
    _restrict_candidate_file_access(sys.argv[1])
    module = _load_candidate(sys.argv[1])
    if request["operation"] == "embed":
        message = np.asarray(request["message_bits"], dtype=np.uint8)
        result = module.embed(image, message, key)
        if not isinstance(result, np.ndarray) or result.dtype != np.uint8 or result.shape != shape:
            raise ValueError("embed must return uint8 RGB image of original shape")
        response = {"shape": list(result.shape), "image_b64": base64.b64encode(result.tobytes()).decode("ascii")}
    elif request["operation"] == "decode":
        result = np.asarray(module.decode(image, key))
        if result.shape != (request["payload_bits"],) or not np.isin(result, [0, 1]).all():
            raise ValueError("decode must return exactly the configured number of binary bits")
        response = {"bits": result.astype(np.uint8).tolist()}
    else:
        raise ValueError("unknown operation")
    print(json.dumps(response, separators=(",", ":")))


if __name__ == "__main__":
    try:
        main()
    except BaseException as error:
        print(json.dumps({"error_type": type(error).__name__, "error": str(error)[:300]}))
        sys.exit(2)
