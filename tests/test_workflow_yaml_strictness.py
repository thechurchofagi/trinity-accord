from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "test_ci_code_alignment.py"


def load_alignment() -> ModuleType:
    spec = importlib.util.spec_from_file_location("workflow_alignment_strictness", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load CI alignment script")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


alignment = load_alignment()


def test_duplicate_workflow_mapping_key_is_rejected(tmp_path: Path) -> None:
    workflow = tmp_path / "duplicate.yml"
    workflow.write_text(
        "name: one\nname: two\non:\n  workflow_dispatch:\n",
        encoding="utf-8",
    )
    with pytest.raises(yaml.YAMLError, match="duplicate key"):
        alignment.load_yaml(workflow)
