#!/usr/bin/env python3
"""TA-REDTEAM-2026-007: token_index schema validation."""
import subprocess, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
res = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'validate_token_index.py'), '--self-test'], cwd=ROOT, text=True, capture_output=True)
if res.stdout: print(res.stdout)
if res.stderr: print(res.stderr, file=sys.stderr)
if res.returncode != 0: sys.exit(res.returncode)
print('TOKEN_INDEX_SCHEMA_VALIDATION_OK')
