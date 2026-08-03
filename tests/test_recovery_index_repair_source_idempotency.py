from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "fix_recovery_index_limitations.py"
EXECUTION_TEST = ROOT / "tests" / "test_repository_preservation_semantics_v3_execution.py"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "fix_recovery_index_limitations_test",
        SCRIPT,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_execution_fixture_normalization_is_byte_idempotent():
    module = load_module()
    current = EXECUTION_TEST.read_text(encoding="utf-8")

    normalized = module.normalize_execution_setup(current)
    assert normalized == current
    assert normalized.count(module.EXECUTION_AUTH_SETUP) == 1
    assert normalized.count(module.EXECUTION_MODULE_SETUP) == 1
    assert module.normalize_execution_setup(normalized) == normalized


def test_execution_fixture_normalization_repairs_repeated_historical_blocks():
    module = load_module()
    current = EXECUTION_TEST.read_text(encoding="utf-8")
    polluted = current.replace(
        module.EXECUTION_AUTH_SETUP,
        module.EXECUTION_AUTH_SETUP * 4,
        1,
    )

    repaired = module.normalize_execution_setup(polluted)
    assert repaired == current
    assert repaired.count(module.EXECUTION_AUTH_SETUP) == 1
    assert module.normalize_execution_setup(repaired) == repaired
