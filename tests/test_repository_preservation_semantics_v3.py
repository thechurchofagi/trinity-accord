from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "preservation/repository-preservation-refresh-authorization.json"
MIGRATION = ROOT / "scripts/migrate_repository_preservation_semantics_v3.py"
RUNNER = ROOT / "scripts/run_repository_preservation_semantics_v3_ci.sh"


def test_semantic_migration_and_runner_are_strict_and_idempotent():
    subprocess.run(["bash", "-n", str(RUNNER)], cwd=ROOT, check=True)
    migration = MIGRATION.read_text(encoding="utf-8")
    runner = RUNNER.read_text(encoding="utf-8")
    assert "fully consumed sequence-2 state" in migration
    assert "sequence-3 authorization has invalid status" in migration
    assert "exact_publication_baseline_tree_embedded" in migration
    assert "full_exact_publication_baseline" in migration
    assert "repository_preservation_legacy_state" in migration
    assert "live_main_equivalence_claimed" in migration
    assert "migrate_repository_preservation_semantics_v3.py" in runner
    assert "fix: finalize repository publication-baseline semantics" in runner
    assert "exec bash scripts/run_repository_preservation_refresh_ci.sh" in runner


def test_sequence_three_state_has_no_moving_main_semantic_leaks():
    auth = json.loads(AUTH.read_text(encoding="utf-8"))
    if auth.get("sequence") != 3:
        assert auth.get("sequence") == 2
        assert auth.get("status") == "consumed"
        return

    recovery = (ROOT / "RECOVERY.md").read_text(encoding="utf-8")
    builder = (ROOT / "scripts/build_preservation_capsule.py").read_text(
        encoding="utf-8"
    )
    verifier = (ROOT / "scripts/preservation_capsule.py").read_text(
        encoding="utf-8"
    )
    restore = (ROOT / "scripts/restore_preservation_capsule.py").read_text(
        encoding="utf-8"
    )
    index = json.loads((ROOT / "api/recovery-index.json").read_text())

    assert "repository-preservation-state-v2.json" in recovery
    assert "historical v1" in recovery
    assert "compatibility" in recovery
    assert "exact declared publication-baseline tree" in recovery
    assert "exact_publication_baseline_tree_embedded" in builder
    assert '"live_main_equivalence_claimed": False' in builder
    assert "publication-baseline capsule overclaims live-main equivalence" in verifier
    assert "full_exact_publication_baseline" in restore
    assert "current Git-tracked production tree" not in restore
    assert index["recovery_entrypoints"]["repository_preservation_state"] == (
        "preservation/repository-preservation-state-v2.json"
    )
    assert index["recovery_entrypoints"]["repository_preservation_legacy_state"] == (
        "preservation/zenodo-state.json"
    )
