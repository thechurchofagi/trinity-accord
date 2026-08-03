from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "scripts/migrate_repository_preservation_semantics_v3.py"

PATHS = {
    "AUTH": "preservation/repository-preservation-refresh-authorization.json",
    "STATE": "preservation/repository-preservation-state-v2.json",
    "PREPARED": "preservation/repository-preservation-refresh-prepared.json",
    "CATALOG": "preservation/recovery-catalog.json",
    "INDEX": "api/recovery-index.json",
    "RECOVERY": "RECOVERY.md",
    "BUILD": "scripts/build_preservation_capsule.py",
    "VERIFY": "scripts/preservation_capsule.py",
    "RESTORE": "scripts/restore_preservation_capsule.py",
    "REFRESH": "scripts/repository_preservation_refresh.py",
    "CAPSULE_TEST": "tests/test_preservation_capsule.py",
    "REFRESH_TEST": "tests/test_repository_preservation_refresh_contract.py",
}


def load_module():
    spec = importlib.util.spec_from_file_location("semantics_v3_migration", MIGRATION)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_migration_executes_twice_idempotently_on_current_consumed_state(tmp_path):
    for relative in PATHS.values():
        source = ROOT / relative
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.exists():
            shutil.copy2(source, target)

    auth_path = tmp_path / PATHS["AUTH"]
    legacy_auth = json.loads(auth_path.read_text(encoding="utf-8"))
    legacy_auth["sequence"] = 2
    legacy_auth["status"] = "consumed"
    auth_path.write_text(
        json.dumps(legacy_auth, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    auth_path = tmp_path / PATHS["AUTH"]
    legacy_auth = json.loads(auth_path.read_text(encoding="utf-8"))
    legacy_auth["sequence"] = 2
    legacy_auth["status"] = "consumed"
    auth_path.write_text(
        json.dumps(legacy_auth, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    auth_path = tmp_path / PATHS["AUTH"]
    legacy_auth = json.loads(auth_path.read_text(encoding="utf-8"))
    legacy_auth["sequence"] = 2
    legacy_auth["status"] = "consumed"
    auth_path.write_text(
        json.dumps(legacy_auth, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    auth_path = tmp_path / PATHS["AUTH"]
    legacy_auth = json.loads(auth_path.read_text(encoding="utf-8"))
    legacy_auth["sequence"] = 2
    legacy_auth["status"] = "consumed"
    auth_path.write_text(
        json.dumps(legacy_auth, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    module = load_module()
    module.ROOT = tmp_path
    for name, relative in PATHS.items():
        setattr(module, name, tmp_path / relative)

    assert module.main() == 0
    assert module.main() == 0

    auth = json.loads((tmp_path / PATHS["AUTH"]).read_text(encoding="utf-8"))
    state = json.loads((tmp_path / PATHS["STATE"]).read_text(encoding="utf-8"))
    index = json.loads((tmp_path / PATHS["INDEX"]).read_text(encoding="utf-8"))
    builder = (tmp_path / PATHS["BUILD"]).read_text(encoding="utf-8")
    verifier = (tmp_path / PATHS["VERIFY"]).read_text(encoding="utf-8")
    restore = (tmp_path / PATHS["RESTORE"]).read_text(encoding="utf-8")
    refresh = (tmp_path / PATHS["REFRESH"]).read_text(encoding="utf-8")
    recovery = (tmp_path / PATHS["RECOVERY"]).read_text(encoding="utf-8")

    assert auth["sequence"] == 3
    assert auth["status"] == "pending"
    assert auth["previous_core_version_doi"] == "10.5281/zenodo.21755655"
    assert state["publication_status"] == "semantic_refresh_authorized"
    assert not (tmp_path / PATHS["PREPARED"]).exists()
    assert index["recovery_entrypoints"]["repository_preservation_state"] == (
        "preservation/repository-preservation-state-v2.json"
    )
    assert index["recovery_entrypoints"]["repository_preservation_legacy_state"] == (
        "preservation/zenodo-state.json"
    )
    assert "exact_publication_baseline_tree_embedded" in builder
    assert "exact_current_production_tree_embedded\": True" not in builder
    assert "publication-baseline capsule overclaims live-main equivalence" in verifier
    assert "full_exact_publication_baseline" in restore
    assert "full_current_git_tracked_tree" not in restore
    assert "EXPECTED_PREVIOUS_DOI = \"10.5281/zenodo.21755655\"" in refresh
    assert "PUBLISH_TRINITY_REPOSITORY_CAPSULE_REFRESH_V3" in refresh
    assert "historical v1" in recovery
    assert "the exact current production tree" not in recovery
