#!/usr/bin/env python3
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
core = HERE / 'verify-chronicle-sidechain-evidence-core.py'
diag = HERE / 'diagnose-chronicle-sidechain-l1.py'

result = subprocess.run([sys.executable, str(core)], check=False)
if result.returncode != 0:
    diagnostic = subprocess.run([sys.executable, str(diag)], check=False)
    if diagnostic.returncode != 0:
        print(f'[L1 DIAG WARNING] diagnostic helper exited {diagnostic.returncode}', file=sys.stderr, flush=True)
raise SystemExit(result.returncode)
