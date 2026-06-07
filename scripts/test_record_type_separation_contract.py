#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "apps/record_chain_intake_gateway/gateway/validation.py"
FINALIZER = ROOT / "scripts/finalize_mainnet_prelaunch_record_from_submission.py"

def require(cond: bool, msg: str) -> None:
    if not cond:
        raise SystemExit(msg)

def main() -> int:
    validation = VALIDATION.read_text(encoding="utf-8")
    finalizer = FINALIZER.read_text(encoding="utf-8")

    require("validate_record_type_separation" in validation, "gateway must define validate_record_type_separation")
    require("RECORD_TYPE_SEPARATION_VIOLATION" in validation, "gateway must emit RECORD_TYPE_SEPARATION_VIOLATION")
    require("_GUARDIAN_APPLICATION_ONLY_KEYS" in validation, "gateway must define guardian-only keys")
    require("optional_linked_guardian_application_request" in validation, "linked guardian request must be treated as guardian-only")
    require("validate_record_type_separation(rt, draft)" in validation, "validate_submission must call validate_record_type_separation")
    require("diagnostics.extend(validate_linked_guardian_request(draft))" not in validation, "legacy linked guardian validator must not be called")

    require("assert_record_type_separation" in finalizer, "finalizer must enforce record type separation")
    require("optional_linked_guardian_application_request" in finalizer, "finalizer must reject linked guardian request")
    require("assert_record_type_separation(submission)" in finalizer, "finalizer must call assert_record_type_separation")

    print("PASS: record type separation contract")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
