from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SECURE_ENTRYPOINT = (
    ROOT / "apps" / "record_chain_intake_gateway" / "secure_entrypoint.py"
)


def test_protected_receipt_envelope_call_binds_verification_flags() -> None:
    """Prevent protected/core receipt-envelope signature drift in production."""
    tree = ast.parse(SECURE_ENTRYPOINT.read_text(encoding="utf-8"))
    calls: list[ast.Call] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "_build_receipt_envelope":
            calls.append(node)

    assert len(calls) == 1, "expected one protected receipt-envelope composition call"
    keyword_names = {keyword.arg for keyword in calls[0].keywords}
    assert "receipt_url_binding_verified" in keyword_names
    assert "stored_submission_hash_verified" in keyword_names
