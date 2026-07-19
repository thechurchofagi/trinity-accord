"""Permanent coverage guard for deterministic Chronicle artifacts."""

from pathlib import Path


def test_required_current_ci_runs_chronicle_drift_group() -> None:
    root = Path(__file__).resolve().parents[1]
    runner = (root / "scripts/run_current_system_tests.py").read_text(encoding="utf-8")
    assert '[sys.executable, "scripts/run_ci_group.py", "chronicle"]' in runner
    workflow = (root / ".github/workflows/run-current-tests.yml").read_text(
        encoding="utf-8"
    )
    assert "python3 scripts/run_current_system_tests.py" in workflow
