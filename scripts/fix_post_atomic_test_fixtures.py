#!/usr/bin/env python3
from pathlib import Path

idempotency_path = Path("apps/record_chain_intake_gateway/tests/test_idempotency_index.py")
text = idempotency_path.read_text(encoding="utf-8")
old = '''        "intake_submission_path": index["intake_submission_path"],
    }
'''
new = '''        "intake_submission_path": index["intake_submission_path"],
        "record_type": index["record_type"],
    }
'''
if text.count(old) != 1:
    raise SystemExit(f"expected one receipt fixture target, found {text.count(old)}")
idempotency_path.write_text(text.replace(old, new, 1), encoding="utf-8")

p0_path = Path("scripts/test_record_chain_p0_transaction_and_finalizer_contract.py")
p0 = p0_path.read_text(encoding="utf-8")
old_contract = '''        "AtomicCreateConflict",
        "exact_after_error",
'''
new_contract = '''        "AtomicCreateConflict",
        "_reconcile_atomic_write(",
        "_commit_reachable_from_head(",
        '"equivalent_tree"',
'''
if p0.count(old_contract) != 1:
    raise SystemExit(f"expected one P0 atomic reconciliation target, found {p0.count(old_contract)}")
p0_path.write_text(p0.replace(old_contract, new_contract, 1), encoding="utf-8")
print("POST_ATOMIC_TEST_CONTRACTS_ALIGNED")
