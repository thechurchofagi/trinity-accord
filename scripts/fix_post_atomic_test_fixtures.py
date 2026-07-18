#!/usr/bin/env python3
from pathlib import Path

path = Path("apps/record_chain_intake_gateway/tests/test_idempotency_index.py")
text = path.read_text(encoding="utf-8")
old = '''        "intake_submission_path": index["intake_submission_path"],
    }
'''
new = '''        "intake_submission_path": index["intake_submission_path"],
        "record_type": index["record_type"],
    }
'''
if text.count(old) != 1:
    raise SystemExit(f"expected one receipt fixture target, found {text.count(old)}")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("POST_ATOMIC_TEST_FIXTURES_ALIGNED")
