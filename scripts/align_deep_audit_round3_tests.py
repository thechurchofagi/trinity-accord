#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: str, old: str, new: str) -> None:
    p = ROOT / path
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one fixture target, found {count}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


DEEP = "apps/record_chain_intake_gateway/tests/test_deep_transaction_recovery.py"
IDEMPOTENCY = "apps/record_chain_intake_gateway/tests/test_idempotency_index.py"

replace_once(
    DEEP,
    '''    final_path = "record-chain/records/R-000000001.json"
    status = {
''',
    '''    final_path = "record-chain/records/R-000000001.json"
    final_record = {"record_id": "R-000000001", "record_type": "echo"}
    final_record["record_sha256"] = app_module._record_chain_record_sha256(final_record)
    status = {
''',
)
replace_once(
    DEEP,
    '''        "final_record_sha256": "a" * 64,
''',
    '''        "final_record_sha256": final_record["record_sha256"],
''',
)
replace_once(
    DEEP,
    '''        if path == final_path:
            return json.dumps({"record_id": "R-000000001", "record_sha256": "a" * 64})
''',
    '''        if path == final_path:
            return json.dumps(final_record)
''',
)

# The second final-status test starts with the same final_path marker after the
# first replacement has consumed the first occurrence.
replace_once(
    DEEP,
    '''    final_path = "record-chain/records/R-000000001.json"
    status = {
''',
    '''    final_path = "record-chain/records/R-000000001.json"
    final_record = {"record_id": "R-000000001", "record_type": "echo"}
    final_record["record_sha256"] = app_module._record_chain_record_sha256(final_record)
    status = {
''',
)
replace_once(
    DEEP,
    '''        "final_record_sha256": "a" * 64,
''',
    '''        "final_record_sha256": final_record["record_sha256"],
''',
)
replace_once(
    DEEP,
    '''        if path == final_path:
            return json.dumps({"record_id": "R-000000001", "record_sha256": "b" * 64})
''',
    '''        if path == final_path:
            forged = dict(final_record)
            forged["record_type"] = "verification"
            return json.dumps(forged)
''',
)

replace_once(
    IDEMPOTENCY,
    '''        final_path = "record-chain/records/R-000000123.json"
        status_path = f"record-chain/receipt-status/{index['receipt_id']}.json"
        status = {
''',
    '''        final_path = "record-chain/records/R-000000123.json"
        final_record = {"record_id": "R-000000123", "record_type": "echo"}
        final_record["record_sha256"] = app_module._record_chain_record_sha256(final_record)
        status_path = f"record-chain/receipt-status/{index['receipt_id']}.json"
        status = {
''',
)
replace_once(
    IDEMPOTENCY,
    '''            "final_record_sha256": "c" * 64,
''',
    '''            "final_record_sha256": final_record["record_sha256"],
''',
)
replace_once(
    IDEMPOTENCY,
    '''            if path == final_path:
                return json.dumps({
                    "record_id": "R-000000123",
                    "record_sha256": "c" * 64,
                })
''',
    '''            if path == final_path:
                return json.dumps(final_record)
''',
)

print("DEEP_AUDIT_ROUND3_TEST_FIXTURES_ALIGNED")
