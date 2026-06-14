#!/usr/bin/env python3
"""Phase 6B Record-Chain Hotfix tests.

Tests:
  1. Builder/generated pending append → record includes authorship_verification_status.
  2. verify fails formal record missing authorship_verification_status.
  3. verify fails oath hash missing/invalid.
  4. verify fails linked Guardian without guardian_stewardship_v1.
  5. append --all continues after one rejected pending.
  6. rejection reason file is written.
  7. raw readback_text in record fails verify.
"""
from __future__ import annotations

import base64
import json
import shutil
import sys
import tempfile

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
CHAIN = ROOT / "record-chain"
RECORDS = CHAIN / "records"
PENDING = CHAIN / "pending"
PROCESSED = CHAIN / "processed"
REJECTED = CHAIN / "rejected"
GENESIS = CHAIN / "genesis"
CHAIN_TIP = CHAIN / "chain-tip.json"
POLICIES = CHAIN / "policies"
SCHEMAS = CHAIN / "schemas"

sys.path.insert(0, str(SCRIPTS))
import trinity_record_chain as mod

sys.path.insert(0, str(ROOT / "apps" / "record_chain_intake_gateway"))
from gateway.authorship import public_key_sha256_from_pem, strip_authorship_for_signing  # noqa: E402
from gateway.canonical import canonical_bytes, sha256_bytes  # noqa: E402

# Re-export for convenience
ensure_dirs = mod.ensure_dirs
verify_native_records = mod.verify_native_records
normalize_record_draft = mod.normalize_record_draft
append_records = mod.append_records
write_json = mod.write_json
read_json = mod.read_json
utc_now = mod.utc_now
content_hash = mod.content_hash
record_hash = mod.record_hash
record_id = mod.record_id
BOUNDARY = mod.BOUNDARY
CHAIN_ID = mod.CHAIN_ID
FORMAL_RECORD_TYPES = mod.FORMAL_RECORD_TYPES
init_policies = mod.init_policies


def _attach_valid_authorship_proof(draft: dict) -> dict:
    """Attach a real in-memory Ed25519 authorship proof to a pending draft.

    The private key is generated only in memory and is never written to disk.
    """
    draft = dict(draft)
    draft.pop("authorship_proof", None)

    # Strip unsigned projection fields before signing, matching production
    # sanitize_pending_record_for_append() behavior.
    from gateway.authorship import strip_unsigned_projection_fields, UNSIGNED_PROJECTION_FIELDS
    draft = strip_unsigned_projection_fields(draft)

    # Pre-add non-projection fields that normalize_record_draft sets via setdefault.
    # Do NOT add back projection fields (chain_id, schema, etc.) as they are stripped.
    draft.setdefault("created_at", utc_now())
    draft.setdefault("what_i_checked", [])
    draft.setdefault("limitations", [])
    draft.setdefault("related_records", [])
    draft.setdefault("immutability_policy", {
        "append_only": True,
        "record_may_be_corrected_by_later_record": True,
        "record_may_not_be_deleted_or_mutated": True,
    })
    draft.setdefault("boundary_acknowledgement", dict(BOUNDARY))

    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    public_key_pem = public_key.public_bytes(
        encoding=Encoding.PEM,
        format=PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")

    payload = canonical_bytes(strip_authorship_for_signing(draft))
    payload_sha256 = sha256_bytes(payload)
    signature_base64 = base64.b64encode(private_key.sign(payload)).decode("ascii")

    draft["authorship_proof"] = {
        "schema": "trinityaccord.agent-authorship-proof.v1",
        "method": "public_key_signature",
        "algorithm": "ed25519",
        "public_key_pem": public_key_pem,
        "public_key_sha256": public_key_sha256_from_pem(public_key_pem),
        "signed_payload_sha256": payload_sha256,
        "signed_message": payload_sha256,
        "signature_base64": signature_base64,
        "claim_boundary": {
            "not authority": True,
            "not attestation": True,
            "not amendment": True,
        },
    }
    return draft


def _make_echo_draft(index: int = 1) -> dict:
    """Build a minimal valid echo draft with real Ed25519 authorship proof.

    Uses v2-style submitting_participant_identity (not actor_identity)
    so that after strip_unsigned_projection_fields, normalize_record_draft
    can derive actor_identity from submitting_participant_identity.
    """
    draft = {
        "schema": "trinityaccord.record-chain-entry-draft.v2",
        "record_type": "echo",
        "created_at": utc_now(),
        "submitting_participant_identity": {
            "participant_type": "agent",
            "participant_public_display_label": "Test Agent",
            "participant_self_declared_identifier": "test-001",
            "participant_identifier_disclosure_status": "not_available",
            "participant_identity_disclosure_preference": "key_continuity_only",
            "participant_provider_or_platform": "Test Runtime",
            "participant_model_or_runtime": "Test Runtime",
            "participant_public_key_sha256": "",
            "human_operator_context": {
                "human_operator_involved": False,
                "human_real_name_disclosure_status": "not_applicable",
                "human_public_display_name": "",
                "human_pseudonym_or_role_label": "",
                "human_private_name_submitted": False,
                "human_private_name_commitment_sha256": "",
            },
        },
        "context_readiness": {
            "declared_context_level": "CC-0",
            "minimum_required_for_action": "CC-0",
            "context_sufficient_for_selected_action": False,
            "loaded_context_urls": [],
            "context_readiness_notes": "",
        },
        "echo_content": {
            "echo_text": "Phase 6B test echo",
            "echo_intent": "recognition",
        },
    }
    return _attach_valid_authorship_proof(draft)



def _make_guardian_draft(index: int = 1) -> dict:
    """Build a minimal valid guardian_application draft with real Ed25519 proof."""
    draft = {
        "schema": "trinityaccord.record-chain-entry-draft.v2",
        "record_type": "guardian_application",
        "created_at": utc_now(),
        "submitting_participant_identity": {
            "participant_type": "agent",
            "participant_public_display_label": "Test Guardian",
            "participant_self_declared_identifier": "guardian-001",
            "participant_identifier_disclosure_status": "not_available",
            "participant_identity_disclosure_preference": "key_continuity_only",
            "participant_provider_or_platform": "Test Runtime",
            "participant_model_or_runtime": "Test Runtime",
            "participant_public_key_sha256": "",
            "human_operator_context": {
                "human_operator_involved": False,
                "human_real_name_disclosure_status": "not_applicable",
                "human_public_display_name": "",
                "human_pseudonym_or_role_label": "",
                "human_private_name_submitted": False,
                "human_private_name_commitment_sha256": "",
            },
        },
        "context_readiness": {
            "declared_context_level": "CC-0",
            "minimum_required_for_action": "CC-0",
            "context_sufficient_for_selected_action": False,
            "loaded_context_urls": [],
            "context_readiness_notes": "",
        },
        "guardian_application_content": {
            "requested_guardian_identifier": "G-00200",
            "guardian_public_key_sha256": "b" * 64,
            "guardian_stewardship_oath": "I solemnly pledge...",
            "guardian_understands_role_is_non_governing": True,
            "guardian_understands_role_is_not_authority": True,
            "guardian_understands_retirement_does_not_delete_history": True,
        },
    }
    return _attach_valid_authorship_proof(draft)



def _setup_chain() -> Path:
    """Create a temporary chain structure and return the temp root."""
    tmp = Path(tempfile.mkdtemp(prefix="phase6b-test-"))
    # Monkey-patch globals
    mod.ROOT = tmp
    mod.CHAIN = tmp / "record-chain"
    mod.GENESIS = mod.CHAIN / "genesis"
    mod.LEGACY_RECORDS = mod.GENESIS / "legacy-records"
    mod.RECORDS = mod.CHAIN / "records"
    mod.PENDING = mod.CHAIN / "pending"
    mod.PROCESSED = mod.CHAIN / "processed"
    mod.REJECTED = mod.CHAIN / "rejected"
    mod.BATCHES = mod.CHAIN / "batches"
    mod.INDEXES = mod.CHAIN / "indexes"
    mod.POLICIES = mod.CHAIN / "policies"
    mod.SCHEMAS = mod.CHAIN / "schemas"
    mod.CHAIN_TIP = mod.CHAIN / "chain-tip.json"
    mod.ANCHORS = mod.CHAIN / "anchors"
    mod.ARWEAVE_ARCHIVES = mod.CHAIN / "arweave-archives"
    mod.ANCHOR_STATUS_API = tmp / "api" / "record-chain-anchor-status.json"
    mod.ARWEAVE_INDEX_API = tmp / "api" / "record-chain-arweave-index.json"
    mod.GUARDIAN_REGISTRY = tmp / "api" / "guardian-registry.json"
    mod.ensure_dirs()
    # Minimal genesis
    genesis_manifest = {
        "schema": "trinityaccord.record-batch-manifest.v1",
        "batch_id": "genesis",
        "batch_manifest_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    }
    mod.write_json(mod.GENESIS / "genesis-batch-manifest.json", genesis_manifest)
    mod.CHAIN_TIP.write_text(json.dumps({
        "schema": "trinityaccord.chain-tip.v1",
        "native_record_count": 0,
        "latest_record_index": 0,
        "latest_record_id": None,
        "latest_record_sha256": None,
        "genesis_batch_manifest_sha256": genesis_manifest["batch_manifest_sha256"],
        "latest_batch_manifest_sha256": genesis_manifest["batch_manifest_sha256"],
        "updated_at": mod.utc_now(),
    }, indent=2), encoding="utf-8")
    return tmp


def _cleanup(tmp: Path) -> None:
    shutil.rmtree(tmp, ignore_errors=True)


def _check_1_append_includes_authorship_verification_status() -> list[str]:
    """After append, formal record includes authorship_verification_status."""
    errors = []
    tmp = _setup_chain()
    try:
        draft = _make_echo_draft()
        mod.write_json(mod.PENDING / "test-echo-001.json", draft)
        mod.append_records(all_records=False)
        recs = sorted(mod.RECORDS.glob("R-*.json"))
        if not recs:
            errors.append("No records after append")
            return errors
        rec = mod.read_json(recs[-1])
        avs = rec.get("authorship_verification_status")
        if not isinstance(avs, dict):
            errors.append("Missing authorship_verification_status")
        else:
            if avs.get("signed_payload_scope") != "pre_append_record_draft":
                errors.append(f"wrong signed_payload_scope: {avs.get('signed_payload_scope')}")
            if avs.get("verified_by_append_before_record") is not True:
                errors.append("verified_by_append_before_record not true")
            if avs.get("final_record_contains_append_assigned_fields_not_in_signed_payload") is not True:
                errors.append("final_record_contains_append_assigned_fields_not_in_signed_payload not true")
        # append_assigned_metadata must NOT contain hash fields
        aam = rec.get("append_assigned_metadata")
        if not isinstance(aam, dict):
            errors.append("Missing append_assigned_metadata")
        else:
            if "content_sha256" in aam:
                errors.append("append_assigned_metadata must not contain content_sha256")
            if "record_sha256" in aam:
                errors.append("append_assigned_metadata must not contain record_sha256")
    finally:
        _cleanup(tmp)
    return errors


def _check_2_verify_fails_missing_authorship_verification_status() -> list[str]:
    """verify_native_records fails if formal record lacks authorship_verification_status."""
    errors = []
    tmp = _setup_chain()
    try:
        draft = _make_echo_draft()
        mod.write_json(mod.PENDING / "test-echo-001.json", draft)
        mod.append_records(all_records=False)
        recs = sorted(mod.RECORDS.glob("R-*.json"))
        if not recs:
            errors.append("No records after append")
            return errors
        rec = mod.read_json(recs[-1])
        del rec["authorship_verification_status"]
        # Re-compute hashes so hash checks pass; only avs check should fail
        rec["content_sha256"] = mod.content_hash(rec)
        rec["record_sha256"] = mod.record_hash(rec)
        mod.write_json(recs[-1], rec)
        verrors = mod.verify_native_records()
        avs_errors = [e for e in verrors if "authorship_verification_status" in e]
        if not avs_errors:
            errors.append("verify should have failed for missing authorship_verification_status")
    finally:
        _cleanup(tmp)
    return errors


def _check_3_verify_fails_oath_hash_missing() -> list[str]:
    """verify fails when oath hash fields are missing or invalid."""
    errors = []
    tmp = _setup_chain()
    try:
        draft = _make_echo_draft()
        draft["submission_oath_verification"] = {
            "oath_read": True,
            "participant_readback_provided": True,
            "readback_matches_canonical_oath": True,
            "no_shortcut_oath_acknowledged": True,
            "oath_does_not_prove_subjective_understanding": True,
            "oath_verifies_exact_readback_only": True,
            "not_authority": True,
            "not_governance": True,
            "not_attestation": True,
            "not_amendment": True,
            "bitcoin_originals_prevail": True,
            # Missing: oath_policy_sha256, canonical_oath_text_sha256,
            # participant_readback_sha256, oath_modules
        }
        # Write record directly (bypass append's post-verify gate) to test
        # verify_native_records() in isolation.
        draft = mod.normalize_record_draft(draft)
        draft["record_index"] = 1
        draft["record_id"] = mod.record_id(1)
        draft["assigned_at"] = mod.utc_now()
        draft["previous_record_sha256"] = None
        draft["content_sha256"] = mod.content_hash(draft)
        draft["record_sha256"] = mod.record_hash(draft)
        mod.write_json(mod.RECORDS / "R-000000001.json", draft)
        verrors = mod.verify_native_records()
        hash_errors = [e for e in verrors if "oath_policy_sha256" in e or "canonical_oath_text_sha256" in e or "participant_readback_sha256" in e]
        module_errors = [e for e in verrors if "oath_modules" in e]
        if not hash_errors:
            errors.append("verify should have failed for missing oath hashes")
        if not module_errors:
            errors.append("verify should have failed for missing oath_modules")
    finally:
        _cleanup(tmp)
    return errors


def _check_4_verify_fails_guardian_without_stewardship() -> list[str]:
    """verify fails when guardian_application oath lacks guardian_stewardship_v1."""
    errors = []
    tmp = _setup_chain()
    try:
        draft = _make_guardian_draft()
        draft["submission_oath_verification"] = {
            "oath_read": True,
            "participant_readback_provided": True,
            "readback_matches_canonical_oath": True,
            "no_shortcut_oath_acknowledged": True,
            "oath_does_not_prove_subjective_understanding": True,
            "oath_verifies_exact_readback_only": True,
            "not_authority": True,
            "not_governance": True,
            "not_attestation": True,
            "not_amendment": True,
            "bitcoin_originals_prevail": True,
            "oath_policy_sha256": "a" * 64,
            "canonical_oath_text_sha256": "b" * 64,
            "participant_readback_sha256": "c" * 64,
            "oath_modules": ["common_submission_integrity_v1"],  # Missing guardian_stewardship_v1
        }
        # Write directly to test verify in isolation
        draft = mod.normalize_record_draft(draft)
        draft["record_index"] = 1
        draft["record_id"] = mod.record_id(1)
        draft["assigned_at"] = mod.utc_now()
        draft["previous_record_sha256"] = None
        draft["content_sha256"] = mod.content_hash(draft)
        draft["record_sha256"] = mod.record_hash(draft)
        mod.write_json(mod.RECORDS / "R-000000001.json", draft)
        verrors = mod.verify_native_records()
        steward_errors = [e for e in verrors if "guardian_stewardship_v1" in e]
        if not steward_errors:
            errors.append("verify should have failed for guardian_application missing guardian_stewardship_v1")
    finally:
        _cleanup(tmp)
    return errors


def _check_5_append_all_continues_after_rejection() -> list[str]:
    """append --all continues processing after one pending is rejected."""
    errors = []
    tmp = _setup_chain()
    try:
        # Good pending
        good = _make_echo_draft()
        mod.write_json(mod.PENDING / "good-001.json", good)
        # Bad pending (missing required fields)
        bad = {"record_type": "echo", "schema": "trinityaccord.record-chain-entry.v1"}
        mod.write_json(mod.PENDING / "bad-001.json", bad)
        mod.append_records(all_records=True)
        recs = sorted(mod.RECORDS.glob("R-*.json"))
        if len(recs) < 1:
            errors.append("Should have appended at least 1 record despite bad pending")
        # Check bad was moved to rejected
        rejected_files = list(mod.REJECTED.glob("bad-001.*"))
        if not rejected_files:
            errors.append("Bad pending should have been moved to rejected/")
    finally:
        _cleanup(tmp)
    return errors


def _check_6_rejection_reason_file_written() -> list[str]:
    """Rejection writes a .rejection.json with reason."""
    errors = []
    tmp = _setup_chain()
    try:
        bad = {"record_type": "echo", "schema": "trinityaccord.record-chain-entry.v1"}
        mod.write_json(mod.PENDING / "bad-only.json", bad)
        mod.append_records(all_records=True)
        rej_path = mod.REJECTED / "bad-only.rejection.json"
        if not rej_path.exists():
            errors.append("rejection.json not written")
        else:
            rej = mod.read_json(rej_path)
            if not rej.get("reason"):
                errors.append("rejection.json missing reason")
            if rej.get("schema") != "trinityaccord.record-chain-rejection.v1":
                errors.append(f"wrong rejection schema: {rej.get('schema')}")
    finally:
        _cleanup(tmp)
    return errors


def _check_7_raw_readback_text_fails_verify() -> list[str]:
    """Raw readback_text in persisted record fails verify."""
    errors = []
    tmp = _setup_chain()
    try:
        draft = _make_echo_draft()
        draft["submission_oath_verification"] = {
            "oath_read": True,
            "participant_readback_provided": True,
            "readback_matches_canonical_oath": True,
            "no_shortcut_oath_acknowledged": True,
            "oath_does_not_prove_subjective_understanding": True,
            "oath_verifies_exact_readback_only": True,
            "not_authority": True,
            "not_governance": True,
            "not_attestation": True,
            "not_amendment": True,
            "bitcoin_originals_prevail": True,
            "oath_policy_sha256": "a" * 64,
            "canonical_oath_text_sha256": "b" * 64,
            "participant_readback_sha256": "c" * 64,
            "oath_modules": ["common_submission_integrity_v1", "echo_integrity_v1"],
            "readback_text": "THIS SHOULD NOT BE HERE",  # FORBIDDEN
        }
        # Write directly to test verify in isolation
        draft = mod.normalize_record_draft(draft)
        draft["record_index"] = 1
        draft["record_id"] = mod.record_id(1)
        draft["assigned_at"] = mod.utc_now()
        draft["previous_record_sha256"] = None
        draft["content_sha256"] = mod.content_hash(draft)
        draft["record_sha256"] = mod.record_hash(draft)
        mod.write_json(mod.RECORDS / "R-000000001.json", draft)
        verrors = mod.verify_native_records()
        readback_errors = [e for e in verrors if "readback_text" in e]
        if not readback_errors:
            errors.append("verify should have failed for raw readback_text in record")
    finally:
        _cleanup(tmp)
    return errors


def _check_8_post_append_verify_passes() -> list[str]:
    """After a successful append, verify_native_records() must pass (post-append gate)."""
    errors = []
    tmp = _setup_chain()
    try:
        draft = _make_echo_draft()
        mod.write_json(mod.PENDING / "test-echo-001.json", draft)
        mod.append_records(all_records=False)
        # If append succeeded without raising, verify should also pass
        # because append_records now calls verify_native_records() internally.
        # Double-check by calling it explicitly.
        verrors = mod.verify_native_records()
        if verrors:
            errors.append(f"verify_native_records failed after successful append: {verrors}")
    finally:
        _cleanup(tmp)
    return errors


def test_1_append_includes_authorship_verification_status() -> None:
    errors = _check_1_append_includes_authorship_verification_status()
    assert not errors, "\n".join(errors)

def test_2_verify_fails_missing_authorship_verification_status() -> None:
    errors = _check_2_verify_fails_missing_authorship_verification_status()
    assert not errors, "\n".join(errors)

def test_3_verify_fails_oath_hash_missing() -> None:
    errors = _check_3_verify_fails_oath_hash_missing()
    assert not errors, "\n".join(errors)

def test_4_verify_fails_guardian_without_stewardship() -> None:
    errors = _check_4_verify_fails_guardian_without_stewardship()
    assert not errors, "\n".join(errors)

def test_5_append_all_continues_after_rejection() -> None:
    errors = _check_5_append_all_continues_after_rejection()
    assert not errors, "\n".join(errors)

def test_6_rejection_reason_file_written() -> None:
    errors = _check_6_rejection_reason_file_written()
    assert not errors, "\n".join(errors)

def test_7_raw_readback_text_fails_verify() -> None:
    errors = _check_7_raw_readback_text_fails_verify()
    assert not errors, "\n".join(errors)

def test_8_post_append_verify_passes() -> None:
    errors = _check_8_post_append_verify_passes()
    assert not errors, "\n".join(errors)

ALL_TESTS = [
    ("append includes authorship_verification_status", _check_1_append_includes_authorship_verification_status),
    ("verify fails missing authorship_verification_status", _check_2_verify_fails_missing_authorship_verification_status),
    ("verify fails oath hash missing/invalid", _check_3_verify_fails_oath_hash_missing),
    ("verify fails guardian without stewardship_v1", _check_4_verify_fails_guardian_without_stewardship),
    ("append --all continues after rejection", _check_5_append_all_continues_after_rejection),
    ("rejection reason file written", _check_6_rejection_reason_file_written),
    ("raw readback_text fails verify", _check_7_raw_readback_text_fails_verify),
    ("post-append verify passes", _check_8_post_append_verify_passes),
]


def main() -> int:
    passed = 0
    failed = 0
    for name, fn in ALL_TESTS:
        errs = fn()
        if errs:
            failed += 1
            print(f"FAIL: {name}")
            for e in errs:
                print(f"  - {e}")
        else:
            passed += 1
            print(f"PASS: {name}")
    print(f"\n{passed}/{passed + failed} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
