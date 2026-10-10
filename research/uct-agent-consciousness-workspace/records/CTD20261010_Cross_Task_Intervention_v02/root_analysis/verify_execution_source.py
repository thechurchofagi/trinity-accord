"""Verify preserved execution bytes and a metadata-only relocation.

No fit is run. The original execution receipt remains unchanged. Current and
historical source files must match their recorded hashes, and their module ASTs
must match after removing only the optional self_check function.
"""
from pathlib import Path
import ast
import hashlib
import json


def core_ast(blob):
    tree = ast.parse(blob.decode("utf-8"))
    tree.body = [
        node for node in tree.body
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        or node.name != "self_check"
    ]
    return ast.dump(tree, include_attributes=False)


def verify_source_provenance(record_root=None, receipt_source_sha256=None):
    root = Path(record_root) if record_root is not None else Path(__file__).resolve().parents[1]
    receipt = json.loads((root / "RELOCATION_PROVENANCE.json").read_text())
    old = (root / receipt["execution_source"]["path"]).read_bytes()
    current = (root / receipt["portable_source"]["path"]).read_bytes()
    old_hash = hashlib.sha256(old).hexdigest()
    current_hash = hashlib.sha256(current).hexdigest()
    assert old_hash == receipt["execution_source"]["sha256"]
    assert current_hash == receipt["portable_source"]["sha256"]
    old_core = core_ast(old)
    current_core = core_ast(current)
    assert old_core == current_core, "Likelihood/fitting module changed beyond self_check"
    core_hash = hashlib.sha256(current_core.encode()).hexdigest()
    assert core_hash == receipt["core_ast_sha256_excluding_self_check"]
    if receipt_source_sha256 is not None:
        # Original stored fits use old_hash; a fresh portable execution may
        # legitimately record current_hash without changing the numerical law.
        assert receipt_source_sha256 in {old_hash, current_hash}
    return {
        "execution_source_sha256": old_hash,
        "current_source_sha256": current_hash,
        "execution_receipt_source_sha256": receipt_source_sha256,
        "core_ast_sha256_excluding_self_check": core_hash,
        "core_ast_identical": True,
        "relocation_provenance": "RELOCATION_PROVENANCE.json",
    }


if __name__ == "__main__":
    print(json.dumps(verify_source_provenance(), indent=2))
