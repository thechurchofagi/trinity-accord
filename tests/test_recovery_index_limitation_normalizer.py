from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/fix_recovery_index_limitations.py"

SANDBOX_PATHS = {
    "REFRESH": "scripts/repository_preservation_refresh.py",
    "INDEX": "api/recovery-index.json",
    "FINAL_STATE_TEST": "tests/test_external_binary_annex_final_state.py",
    "ANNEX_V2_TEST": "tests/test_external_binary_annex_v2.py",
    "CAPSULE_TEST": "tests/test_preservation_capsule.py",
    "SEMANTICS_TEST": "tests/test_repository_preservation_semantics_v3.py",
    "SEMANTICS_EXEC_TEST": "tests/test_repository_preservation_semantics_v3_execution.py",
}


def load_module():
    spec = importlib.util.spec_from_file_location("recovery_index_fix", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def copy_sandbox(tmp_path: Path) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    for name, relative in SANDBOX_PATHS.items():
        source = ROOT / relative
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        paths[name] = target
    return paths


def test_limitation_repair_is_executable_and_idempotent(tmp_path):
    real_before = {
        name: (ROOT / relative).read_bytes()
        for name, relative in SANDBOX_PATHS.items()
    }
    sandbox = copy_sandbox(tmp_path)

    module = load_module()
    module.ROOT = tmp_path
    for name, path in sandbox.items():
        setattr(module, name, path)

    assert module.main() == 0
    after_first = {name: path.read_bytes() for name, path in sandbox.items()}
    assert module.main() == 0
    after_second = {name: path.read_bytes() for name, path in sandbox.items()}
    assert after_second == after_first

    # Regression guard: this test must never mutate the checked-out repository.
    assert {
        name: (ROOT / relative).read_bytes()
        for name, relative in SANDBOX_PATHS.items()
    } == real_before

    refresh = sandbox["REFRESH"]
    index = sandbox["INDEX"]
    source = refresh.read_text(encoding="utf-8")
    value = json.loads(index.read_text(encoding="utf-8"))
    limitations = value["limitations"]

    assert "def normalize_limitations" in source
    assert source.count('index["limitations"] = normalize_limitations(limitations)') == 2
    assert "recovery index limitations are stale or duplicated" in source
    assert len(limitations) == len(set(limitations))
    assert module.LEGACY_TREE_LIMITATION not in limitations
    assert module.BASELINE_TREE_LIMITATION in limitations
    assert limitations.count(module.QUALIFIED_LIMITATION) == 1
    assert value["source_digest"] == module.canonical_digest(value)


def test_later_current_baseline_contract_supersedes_historical_doi_literal(tmp_path):
    sandbox = copy_sandbox(tmp_path)
    module = load_module()
    module.ROOT = tmp_path
    for name, path in sandbox.items():
        setattr(module, name, path)

    annex_source = sandbox["ANNEX_V2_TEST"].read_text(encoding="utf-8")
    assert module.CURRENT_DOI_CONTRACT_SOURCE in annex_source
    assert module.CURRENT_DOI_SUCCESSOR_SOURCE in annex_source
    assert module.CURRENT_DOI_SUCCESSOR_ASSERTION in annex_source
    assert module.CURRENT_DOI_SUCCESSOR_LINEAGE_ASSERTION in annex_source
    assert module.has_current_baseline_doi_contract(annex_source)
    assert module.OLD_CURRENT_DOI_ASSERTION not in annex_source

    # A later sealed successor baseline is already normalized for purposes of this
    # historical repair and must not be rewritten back to an older literal DOI.
    module.normalize_annex_v2_current_doi_assertion()
    assert sandbox["ANNEX_V2_TEST"].read_text(encoding="utf-8") == annex_source
