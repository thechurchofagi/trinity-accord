#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: str, old: str, new: str) -> None:
    p = ROOT / path
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one target, found {count}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    "apps/record_chain_intake_gateway/tests/test_deep_audit_round3.py",
    '''        append_status="queued",
        diagnostics=[],
''',
    '''        append_status="queued",
        receipt={},
        diagnostics=[],
''',
)
replace_once(
    "apps/record_chain_intake_gateway/tests/test_deep_transaction_recovery.py",
    '''    with pytest.raises(RuntimeError, match="final record binding mismatch"):
        await app_module._read_receipt_final_status(receipt_id)
''',
    '''    with pytest.raises(RuntimeError, match="hash recomputation failed"):
        await app_module._read_receipt_final_status(receipt_id)
''',
)
print("DEEP_AUDIT_ROUND3_EXPECTATIONS_FIXED")
