from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/fix_recovery_index_limitations.py"


def load_module():
    spec = importlib.util.spec_from_file_location("recovery_index_fix", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_limitation_repair_is_executable_and_idempotent(tmp_path):
    refresh = tmp_path / "scripts/repository_preservation_refresh.py"
    index = tmp_path / "api/recovery-index.json"
    refresh.parent.mkdir(parents=True)
    index.parent.mkdir(parents=True)
    shutil.copy2(ROOT / "scripts/repository_preservation_refresh.py", refresh)
    shutil.copy2(ROOT / "api/recovery-index.json", index)

    module = load_module()
    module.ROOT = tmp_path
    module.REFRESH = refresh
    module.INDEX = index

    assert module.main() == 0
    assert module.main() == 0

    source = refresh.read_text(encoding="utf-8")
    value = json.loads(index.read_text(encoding="utf-8"))
    limitations = value["limitations"]

    assert "def normalize_limitations" in source
    assert source.count("index[\"limitations\"] = normalize_limitations(limitations)") == 2
    assert "recovery index limitations are stale or duplicated" in source
    assert len(limitations) == len(set(limitations))
    assert module.LEGACY_TREE_LIMITATION not in limitations
    assert module.BASELINE_TREE_LIMITATION in limitations
    assert limitations.count(module.QUALIFIED_LIMITATION) == 1
    assert value["source_digest"] == module.canonical_digest(value)
