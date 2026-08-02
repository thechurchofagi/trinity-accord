from __future__ import annotations

import ast
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/repository_preservation_refresh.py"


def test_repository_preservation_refresh_has_unique_normalizer_definitions():
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"), filename=str(SCRIPT))
    names = Counter(
        node.name for node in tree.body if isinstance(node, ast.FunctionDef)
    )
    assert names["baseline_tree_limitation"] == 1
    assert names["normalize_limitations"] == 1
