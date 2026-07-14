from __future__ import annotations

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_legacy_pointer_coverage() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_legacy_pointer_coverage.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
