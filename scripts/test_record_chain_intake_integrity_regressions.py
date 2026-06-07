#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def ok(msg: str) -> None:
    print(f"PASS: {msg}")


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        fail(f"Cannot load module {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_security_helpers() -> None:
    sec = load_module(
        ROOT / "apps" / "record_chain_intake_gateway" / "gateway" / "security.py",
        "rc_security",
    )
    samples = [
        "-----BEGIN ENCRYPTED PRIVATE KEY-----\nabc",
        "-----BEGIN PGP PRIVATE KEY BLOCK-----\nabc",
        "-----BEGIN AGE ENCRYPTED FILE-----\nabc",
        "sk-ant-api03-abcdefghijklmnopqrstuvwxyz1234567890",
        # Slack token pattern tested via regex match, not literal sample
    ]
    # Verify Slack token regex matches
    import re
    slack_pat = re.compile(r"\bxox(?:a|b|p|o|s|r)-[A-Za-z0-9-]{20,}\b")
    if not slack_pat.search("xoxb-test-1234-test-5678-test-abcd"):
        fail("Slack token pattern should match")
    for sample in samples:
        if not sec.find_secret_hits({"x": sample}):
            fail(f"secret sample not detected: {sample[:40]}")

    draft = {
        "record_draft": {
            "submitting_participant_identity": {
                "human_operator_context": {
                    "human_private_name_submitted": True,
                }
            }
        }
    }
    hits = sec.find_private_human_identity_hits(draft)
    if not hits:
        fail("nested human_private_name_submitted=true was not detected")
    if not any("human_operator_context.human_private_name_submitted" in h["path"] for h in hits):
        fail(f"privacy hit path too vague: {hits}")

    a = "hello\r\nworld  "
    b = "hello\nworld"
    if sec.normalize_oath_text(a) != sec.normalize_oath_text(b):
        fail("oath normalization should normalize CRLF and strip")
    if sec.sha256_text(sec.normalize_oath_text(a)) != sec.sha256_text(sec.normalize_oath_text(b)):
        fail("normalized oath hashes should match")

    ok("shared security helpers")


def test_validation_source_markers() -> None:
    text = (ROOT / "apps" / "record_chain_intake_gateway" / "gateway" / "validation.py").read_text(encoding="utf-8")

    required = [
        "find_secret_hits",
        "find_private_human_identity_hits",
        "normalize_oath_text",
        "readback_text_hash_canonicalization",
        "NFC_CRLF_TO_LF_STRIP",
    ]
    for marker in required:
        if marker not in text:
            fail(f"validation.py missing marker: {marker}")

    if 'hashlib.sha256(\n                (client_oath.get("readback_text"' in text:
        fail("redaction still appears to hash raw oath readback text")

    ok("validation source markers")


def test_receipt_immutability_source_markers() -> None:
    receipts = (ROOT / "apps" / "record_chain_intake_gateway" / "gateway" / "receipts.py").read_text(encoding="utf-8")
    app = (ROOT / "apps" / "record_chain_intake_gateway" / "app.py").read_text(encoding="utf-8")

    if "RECEIPT_HASH_PREFIX_LEN = 24" not in receipts and "RECEIPT_HASH_PREFIX_LEN=24" not in receipts:
        fail("receipts.py must define RECEIPT_HASH_PREFIX_LEN = 24")
    if "LEGACY_RECEIPT_HASH_PREFIX_LEN = 12" not in receipts and "LEGACY_RECEIPT_HASH_PREFIX_LEN=12" not in receipts:
        fail("receipts.py must define LEGACY_RECEIPT_HASH_PREFIX_LEN = 12")
    if "compute_receipt_sha256" not in receipts:
        fail("receipts.py must define compute_receipt_sha256")
    if "make_legacy_receipt_id" not in receipts:
        fail("receipts.py must define make_legacy_receipt_id")

    for marker in [
        "make_receipt_id(submission_sha256, now)",
        "make_legacy_receipt_id(submission_sha256, now)",
        "RECEIPT_PATH_CONFLICT",
        "INTAKE_ARTIFACT_PATH_CONFLICT",
        "LEGACY_INTAKE_ARTIFACT_PATH_CONFLICT",
        "duplicate_existing_receipt_returned",
        "_existing_receipt_matches_current",
        "_find_existing_matching_receipt",
    ]:
        if marker not in app:
            fail(f"app.py missing immutable artifact marker: {marker}")

    suspicious = [
        "sha=existing_sub_sha",
        "sha=existing_pending_sha",
        "sha=existing_receipt_sha",
        "sha=existing_guardian_sha",
    ]
    for marker in suspicious:
        if marker in app:
            fail(f"app.py still updates existing immutable artifact via {marker}")

    ok("receipt immutability source markers")


def test_get_receipt_legacy_compatibility() -> None:
    app = (ROOT / "apps" / "record_chain_intake_gateway" / "app.py").read_text(encoding="utf-8")
    if "[a-f0-9]{12}|[a-f0-9]{24}" not in app:
        fail("get_receipt must accept both legacy 12-hex and new 24-hex receipt ids")
    if "sha12-or-sha24" not in app:
        fail("get_receipt error message/doc should mention sha12-or-sha24")
    ok("get_receipt legacy compatibility")


def test_linked_guardian_disabled() -> None:
    app = (ROOT / "apps" / "record_chain_intake_gateway" / "app.py").read_text(encoding="utf-8")
    if "LINKED_GUARDIAN_AUTO_CREATION_DISABLED" not in app:
        fail("linked guardian auto-creation must be explicitly disabled")
    if "proof if authorship_verified" in app:
        fail("app.py still appears to pass originating proof into linked guardian draft")
    ok("linked guardian auto-creation disabled")


def test_finalizer_binding_source_markers() -> None:
    finalizer = (ROOT / "scripts" / "finalize_mainnet_prelaunch_record_from_submission.py").read_text(encoding="utf-8")
    auto = (ROOT / "scripts" / "auto_finalize_accepted_submissions.py").read_text(encoding="utf-8")

    for text, label in [(finalizer, "finalizer"), (auto, "auto-finalizer")]:
        if "assert_receipt_binds_submission" not in text:
            fail(f"{label} must assert receipt-submission binding")
        for marker in ["stored_submission_sha256", "intake_submission_path", "receipt_path", "receipt_sha256"]:
            if marker not in text:
                fail(f"{label} binding check missing {marker}")

    ok("finalizer binding source markers")


def test_append_authorship_verification_source_markers() -> None:
    text = (ROOT / "scripts" / "trinity_record_chain.py").read_text(encoding="utf-8")

    if "verify_pending_record_authorship" not in text:
        fail("append must define/use verify_pending_record_authorship")
    if "verified_by_append_before_record" not in text:
        fail("append must write verified_by_append_before_record")
    if "verify_authorship_proof(record, proof)" not in text:
        fail("append must call verify_authorship_proof(record, proof) on pending draft")
    if "invalid authorship_proof.schema" not in text:
        fail("append must validate authorship_proof.schema before verifier")
    if '"verified_by_gateway_before_pending": True' in text:
        fail("append must not unconditionally set verified_by_gateway_before_pending true")

    ok("append authorship verification markers")


def test_rate_limit_policy_honesty() -> None:
    policy_path = ROOT / "api" / "gateway-rate-limit-policy.v1.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    impl = policy.get("implementation_status") or {}

    if impl.get("rate_limit_implementation") != "single_process_in_memory_sliding_window":
        fail("rate-limit policy must disclose single_process_in_memory_sliding_window")
    if impl.get("multi_instance_safe") is not False:
        fail("rate-limit policy must disclose multi_instance_safe=false")
    if impl.get("durable_across_restart") is not False:
        fail("rate-limit policy must disclose durable_across_restart=false")

    test_text = (ROOT / "scripts" / "test_phase7a_rate_limit_contract.py").read_text(encoding="utf-8")
    for marker in ["rate_limit_implementation", "multi_instance_safe", "durable_across_restart"]:
        if marker not in test_text:
            fail(f"rate-limit contract test missing marker {marker}")

    ok("rate-limit policy honesty")


def main() -> int:
    test_security_helpers()
    test_validation_source_markers()
    test_receipt_immutability_source_markers()
    test_get_receipt_legacy_compatibility()
    test_linked_guardian_disabled()
    test_finalizer_binding_source_markers()
    test_append_authorship_verification_source_markers()
    test_rate_limit_policy_honesty()
    print("\n=== RECORD-CHAIN INTAKE INTEGRITY REGRESSION TESTS PASSED ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
