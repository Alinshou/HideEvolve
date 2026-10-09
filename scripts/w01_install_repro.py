"""Reproduce W01 installation in a clean environment, retaining actual command logs."""

from datetime import datetime
import importlib.metadata
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "tmp" / "w01-install-repro-20261009"
LOG = ROOT / "repro" / "install.log"


def main():
    if LOG.exists() or TARGET.exists():
        raise SystemExit("Refusing to overwrite an existing installation reproduction.")
    with LOG.open("x", encoding="utf-8") as log:
        log.write("W01 separately dated installation reproduction\n")
        log.write("Original installation transcript was not retained. This is a new reproduction.\n")
        log.write(f"Started: {datetime.now().astimezone().isoformat()}\n")
        log.flush()

        def run(args, cwd=ROOT):
            log.write(f"\nCOMMAND: {subprocess.list2cmdline([str(a) for a in args])}\n")
            log.flush()
            result = subprocess.run([str(a) for a in args], cwd=cwd, stdout=log, stderr=log)
            log.write(f"EXIT_CODE: {result.returncode}\n")
            log.flush()
            print(f"Completed step: exit {result.returncode}", flush=True)
            if result.returncode:
                raise SystemExit(result.returncode)

        run([sys.executable, "-m", "venv", TARGET])
        python = TARGET / "Scripts" / "python.exe"
        run([python, "-m", "pip", "install", "--disable-pip-version-check", "setuptools", "wheel"])
        run([python, "-m", "pip", "install", "--disable-pip-version-check", "-r",
             ROOT / "repro" / "requirements-lock.txt", "-e", ROOT / "third_party" / "ShinkaEvolve",
             "--no-build-isolation"])
        run([python, "-m", "pip", "check"])
        run([python, "-c", "import sys,shinka,importlib.metadata as m; print(sys.version); print(sys.executable); print('ShinkaEvolve',m.version('shinka-evolve'))"])
        run([python, "-m", "pip", "freeze", "--exclude-editable"])
        log.write(f"\nCompleted: {datetime.now().astimezone().isoformat()}\n")
        log.write("RESULT: PASS (installation, import, dependency consistency)\n")
    print(f"Installation evidence: {LOG}")


if __name__ == "__main__":
    main()
