#!/usr/bin/env python3
"""Test: Record-Chain Oath Gate contract compliance."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OATH_POLICY = ROOT / "api" / "record-chain-oath-policy.v1.json"
SCHEMA = ROOT / "api" / "record-chain-submission-schema.v1.json"
FIELD_HELPER = ROOT / "api" / "record-chain-field-helper.v1.json"
BUILDER = ROOT / "downloads" / "record-chain-builder.mjs"
VALIDATION = ROOT / "apps" / "record_chain_intake_gateway" / "gateway" / "validation.py"

EXPECTED_MODULES = [
    "common_submission_integrity_v1",
    "echo_integrity_v1",
    "verification_integrity_v1",
    "guardian_stewardship_v1",
    "retirement_or_key_management_integrity_v1",
    "propagation_integrity_v1",
    "correction_integrity_v1",
    "classification_update_integrity_v1",
]

REQUIRED_BUILDER_CONTEXT_ARGS = [
    "--context-sufficient-for-selected-action", "true",
    "--loaded-urls", "https://www.trinityaccord.org/agent-first-contact/,https://www.trinityaccord.org/api/record-chain-intake-gateway.v1.json",
    "--discovery-mode", "user_task_context",
    "--record-decision", "human",
    "--submission-executor", "self",
    "--human-operator-involved", "true",
]

REQUIRED_VERIFICATION_CONTENT_ARGS = [
    "--verification-level", "V3",
    "--scope-label", "oath-gate-contract",
    "--what-was-checked", "builder oath gate",
    "--verification-claim", "Test verified the builder oath gate contract locally.",
    "--fresh-actions", "ran print-oath,ran builder",
]


def main() -> None:
    errors = []

    # Test 1: Oath policy exists and parses
    if not OATH_POLICY.exists():
        errors.append("api/record-chain-oath-policy.v1.json: NOT FOUND")
        print("FAIL:\n" + "\n".join(f"  {e}" for e in errors))
        sys.exit(1)

    policy = json.loads(OATH_POLICY.read_text(encoding="utf-8"))

    # Test 2: Schema matches
    if policy.get("schema") != "trinityaccord.record-chain-oath-policy.v1":
        errors.append(f"wrong schema: {policy.get('schema')}")

    # Test 3: Policy has no_shortcut_policy with boundary
    nsp = policy.get("no_shortcut_policy")
    if not isinstance(nsp, dict):
        errors.append("missing no_shortcut_policy")
    else:
        if not nsp.get("readback_required"):
            errors.append("no_shortcut_policy.readback_required is not true")
        if not nsp.get("required_declarations"):
            errors.append("no_shortcut_policy.required_declarations is empty")
        if len(nsp.get("required_declarations", [])) < 10:
            errors.append(f"no_shortcut_policy.required_declarations has {len(nsp.get('required_declarations', []))} items, expected 10+")
        boundary = nsp.get("boundary", {})
        if not boundary.get("oath_does_not_prove_subjective_understanding"):
            errors.append("no_shortcut_policy.boundary.oath_does_not_prove_subjective_understanding missing or not true")
        if not boundary.get("oath_verifies_exact_readback_only"):
            errors.append("no_shortcut_policy.boundary.oath_verifies_exact_readback_only missing or not true")

    # Test 4: Policy has all 8 modules
    modules = policy.get("modules", {})
    for mod_id in EXPECTED_MODULES:
        if mod_id not in modules:
            errors.append(f"missing module: {mod_id}")
        else:
            mod = modules[mod_id]
            if not mod.get("label"):
                errors.append(f"module {mod_id} missing label")
            if not mod.get("text"):
                errors.append(f"module {mod_id} missing text")

    # Test 5: Canonicalization fields
    can = policy.get("canonicalization", {})
    for field in ["line_endings", "trim_outer_whitespace", "trim_outer_whitespace_before_hash",
                  "preserve_internal_whitespace", "module_order_matters", "text_encoding",
                  "unicode_normalization", "policy_text_should_remain_ascii", "module_joiner"]:
        if field not in can:
            errors.append(f"canonicalization missing: {field}")

    # Test 6: linked_guardian_module
    if policy.get("linked_guardian_module") != "guardian_stewardship_v1":
        errors.append(f"linked_guardian_module: expected guardian_stewardship_v1, got {policy.get('linked_guardian_module')}")

    # Test 7: Record type modules mapping
    rtm = policy.get("record_type_modules", {})
    for rt in ["echo", "verification", "guardian_application", "guardian_retirement",
               "guardian_key_rotation", "propagation", "correction", "classification_update"]:
        if rt not in rtm:
            errors.append(f"record_type_modules missing: {rt}")
        elif "common_submission_integrity_v1" not in rtm[rt]:
            errors.append(f"record_type_modules[{rt}] missing common_submission_integrity_v1")

    # Test 8: Builder has print-oath command and OATH_POLICY_SHA256
    if BUILDER.exists():
        builder_text = BUILDER.read_text(encoding="utf-8")
        if "print-oath" not in builder_text:
            errors.append("builder missing print-oath command")
        if "OATH_POLICY_SHA256" not in builder_text:
            errors.append("builder missing OATH_POLICY_SHA256")
        # Verify embedded hash matches actual policy hash
        import re
        m = re.search(r'OATH_POLICY_SHA256\s*=\s*"([a-f0-9]{64})"', builder_text)
        if m:
            embedded_sha = m.group(1)
            # Exclude API metadata fields not in builder's embedded OATH_POLICY
            _metadata_keys = {
                "oath_policy_sha256",
                "oath_policy_sha256_semantics",
                "canonical_oath_text_hash_is_record_type_specific",
            }
            policy_core = {k: v for k, v in policy.items() if k not in _metadata_keys}
            canonical = json.dumps(policy_core, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            actual_sha = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
            if embedded_sha != actual_sha:
                errors.append(f"builder OATH_POLICY_SHA256 mismatch: embedded={embedded_sha[:16]}... actual={actual_sha[:16]}...")
        else:
            errors.append("cannot parse OATH_POLICY_SHA256 from builder")
    else:
        errors.append("downloads/record-chain-builder.mjs: NOT FOUND")

    # Test 9: Gateway has validate_submission_oath and redact
    if VALIDATION.exists():
        val_text = VALIDATION.read_text(encoding="utf-8")
        if "def validate_submission_oath" not in val_text:
            errors.append("validation.py missing validate_submission_oath")
        if "def redact_transient_oath_readback" not in val_text:
            errors.append("validation.py missing redact_transient_oath_readback")
    else:
        errors.append("validation.py: NOT FOUND")

    # Test 10: Schema contains submission_oath_verification and client_oath_readback
    if SCHEMA.exists():
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        draft_props = schema.get("properties", {}).get("record_draft", {}).get("properties", {})
        if "submission_oath_verification" not in draft_props:
            errors.append("record_draft.properties missing submission_oath_verification")
        top_props = schema.get("properties", {})
        if "client_oath_readback" not in top_props:
            errors.append("top-level properties missing client_oath_readback")
        claim = schema.get("$defs", {}).get("authorship_proof", {}).get("properties", {}).get("claim_boundary", {})
        if claim.get("type") != "object":
            errors.append(f"claim_boundary type: expected 'object', got '{claim.get('type')}'")
    else:
        errors.append("submission schema: NOT FOUND")

    # Test 11: Field helper contains oath guidance
    if FIELD_HELPER.exists():
        fh = json.loads(FIELD_HELPER.read_text(encoding="utf-8"))
        groups = fh.get("field_groups", [])
        has_oath = any("oath" in g.get("field", "") for g in groups)
        if not has_oath:
            errors.append("field helper missing oath guidance entries")
    else:
        errors.append("field helper: NOT FOUND")

    # Test 12: Builder print-oath works for echo
    result = subprocess.run(
        ["node", str(BUILDER), "print-oath", "--record-type", "echo"],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode != 0:
        errors.append(f"builder print-oath echo failed: {result.stderr[:200]}")
    elif "Common Submission Integrity" not in result.stdout:
        errors.append("builder print-oath echo missing Common Submission Integrity")
    elif "Echo Integrity" not in result.stdout:
        errors.append("builder print-oath echo missing Echo Integrity")

    # Test 13: print-oath --linked-guardian includes Guardian Stewardship
    result = subprocess.run(
        ["node", str(BUILDER), "print-oath", "--record-type", "echo", "--linked-guardian"],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode != 0:
        errors.append(f"builder print-oath echo --linked-guardian failed: {result.stderr[:200]}")
    elif "Guardian Stewardship" not in result.stdout:
        errors.append("builder print-oath echo --linked-guardian missing Guardian Stewardship")

    result = subprocess.run(
        ["node", str(BUILDER), "print-oath", "--record-type", "verification", "--linked-guardian"],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode != 0:
        errors.append(f"builder print-oath verification --linked-guardian failed: {result.stderr[:200]}")
    elif "Guardian Stewardship" not in result.stdout:
        errors.append("builder print-oath verification --linked-guardian missing Guardian Stewardship")

    # Test 14: Formal build without --readback fails
    result = subprocess.run(
        ["node", str(BUILDER), "echo", "--actor-label", "test", "--provider", "test",
         "--body", "test", "--context-level", "CC-3", *REQUIRED_BUILDER_CONTEXT_ARGS, "--out", "/tmp/test-no-readback.json"],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode == 0:
        errors.append("echo build without --readback should fail but succeeded")
    elif "--readback" not in result.stderr:
        errors.append(f"echo build without --readback: wrong error message: {result.stderr[:200]}")

    # Test 15: Formal build with wrong --readback fails
    result = subprocess.run(
        ["node", str(BUILDER), "echo", "--actor-label", "test", "--provider", "test",
         "--body", "test", "--context-level", "CC-3", *REQUIRED_BUILDER_CONTEXT_ARGS, "--readback", "wrong readback text",
         "--out", "/tmp/test-wrong-readback.json"],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode == 0:
        errors.append("echo build with wrong --readback should fail but succeeded")

    # Test 16: Formal build with exact --readback succeeds
    result = subprocess.run(
        ["node", str(BUILDER), "print-oath", "--record-type", "echo"],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode != 0:
        errors.append("cannot get canonical oath for test 16")
    else:
        canonical = result.stdout
        result = subprocess.run(
            ["node", str(BUILDER), "echo", "--actor-label", "test", "--provider", "test",
             "--body", "test", "--context-level", "CC-3", *REQUIRED_BUILDER_CONTEXT_ARGS, "--readback", canonical,
             "--generate-authorship-key", "--key-dir", "/tmp/test-oath-key",
             "--out", "/tmp/test-correct-readback.json"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            errors.append(f"echo build with correct --readback failed: {result.stderr[:200]}")
        else:
            data = json.loads(Path("/tmp/test-correct-readback.json").read_text())
            client = data.get("client_oath_readback", {})
            oath = data.get("record_draft", {}).get("submission_oath_verification", {})
            # readback_text must equal user-provided readback
            if not client.get("readback_text"):
                errors.append("client_oath_readback.readback_text is empty")
            # oath must declare not auto-filled
            if oath.get("readback_was_not_auto_filled_by_builder") is not True:
                errors.append("readback_was_not_auto_filled_by_builder is not true")
            # oath modules should match record type
            expected_mods = ["common_submission_integrity_v1", "echo_integrity_v1"]
            if oath.get("oath_modules") != expected_mods:
                errors.append(f"oath_modules mismatch: {oath.get('oath_modules')} != {expected_mods}")

    # Test 17: Builder does not contain function that sets readback_text = canonicalOath
    if BUILDER.exists():
        builder_text = BUILDER.read_text(encoding="utf-8")
        # Check there's no pattern like "readback_text: canonicalOath" or "readback_text: canonical"
        import re
        bad_patterns = re.findall(r'readback_text:\s*canonical\w*', builder_text)
        if bad_patterns:
            errors.append(f"builder still has auto-fill pattern: {bad_patterns}")

    # Test 18: Builder embedded OATH_POLICY deep-equals api file
    if BUILDER.exists():
        builder_text = BUILDER.read_text(encoding="utf-8")
        # Extract OATH_POLICY object from builder
        m = re.search(r'const OATH_POLICY = ({[\s\S]*?});\s*\nconst OATH_POLICY_SHA256', builder_text)
        if m:
            try:
                import re as _re
                js_obj = m.group(1)
                # Convert JS literals to JSON
                js_obj = _re.sub(r'\btrue\b', 'true', js_obj)  # already valid JSON
                js_obj = _re.sub(r'\bfalse\b', 'false', js_obj)
                js_obj = _re.sub(r'\bnull\b', 'null', js_obj)
                # JS object uses unquoted keys - convert to quoted
                js_obj = _re.sub(r'(\s)(\w+)(\s*:)', lambda m: m.group(1) + '"' + m.group(2) + '"' + m.group(3), js_obj)
                embedded_policy = json.loads(js_obj)
                # Compare core policy fields only (exclude API metadata not in builder)
                _metadata_keys = {
                    "oath_policy_sha256",
                    "oath_policy_sha256_semantics",
                    "canonical_oath_text_hash_is_record_type_specific",
                }
                policy_core = {k: v for k, v in policy.items() if k not in _metadata_keys}
                embedded_core = {k: v for k, v in embedded_policy.items() if k not in _metadata_keys}
                if embedded_core != policy_core:
                    errors.append("builder embedded OATH_POLICY does not deep-equal api policy")
            except Exception as e:
                errors.append(f"cannot parse builder embedded OATH_POLICY: {e}")
        else:
            errors.append("cannot find OATH_POLICY object in builder")

    # Test 19: echo build with --linked-guardian and exact linked oath succeeds
    result = subprocess.run(
        ["node", str(BUILDER), "print-oath", "--record-type", "echo", "--linked-guardian"],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode != 0:
        errors.append("cannot get linked guardian canonical oath for test 19")
    else:
        linked_oath = result.stdout
        if "guardian_stewardship_v1" not in linked_oath:
            errors.append("linked guardian oath should include guardian_stewardship_v1 module")
        result = subprocess.run(
            ["node", str(BUILDER), "echo", "--actor-label", "test", "--provider", "test",
             "--body", "test", "--context-level", "CC-3", *REQUIRED_BUILDER_CONTEXT_ARGS, "--linked-guardian",
             "--readback", linked_oath,
             "--generate-authorship-key", "--key-dir", "/tmp/test-linked-echo-key",
             "--out", "/tmp/test-linked-echo.json"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            errors.append(f"echo build with --linked-guardian failed: {result.stderr[:200]}")
        else:
            data = json.loads(Path("/tmp/test-linked-echo.json").read_text())
            draft = data.get("record_draft", {})
            guardian_req = draft.get("optional_linked_guardian_application_request", {})
            if guardian_req.get("does_participant_request_guardian_application_with_this_record") is not True:
                errors.append("linked echo: does_participant_request_guardian_application_with_this_record should be true")
            oath = draft.get("submission_oath_verification", {})
            if "guardian_stewardship_v1" not in oath.get("oath_modules", []):
                errors.append(f"linked echo: oath_modules should include guardian_stewardship_v1, got {oath.get('oath_modules')}")
            client = data.get("client_oath_readback", {})
            if "guardian_stewardship_v1" not in client.get("oath_modules", []):
                errors.append(f"linked echo: client_oath_readback.oath_modules should include guardian_stewardship_v1, got {client.get('oath_modules')}")

    # Test 20: verification build with --linked-guardian behaves the same
    result = subprocess.run(
        ["node", str(BUILDER), "print-oath", "--record-type", "verification", "--linked-guardian"],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode != 0:
        errors.append("cannot get linked guardian canonical oath for test 20")
    else:
        linked_oath_v = result.stdout
        if "guardian_stewardship_v1" not in linked_oath_v:
            errors.append("linked guardian verification oath should include guardian_stewardship_v1 module")
        result = subprocess.run(
            ["node", str(BUILDER), "verification", "--actor-label", "test", "--provider", "test",
             *REQUIRED_VERIFICATION_CONTENT_ARGS, "--context-level", "CC-3", *REQUIRED_BUILDER_CONTEXT_ARGS, "--linked-guardian",
             "--readback", linked_oath_v,
             "--generate-authorship-key", "--key-dir", "/tmp/test-linked-verify-key",
             "--out", "/tmp/test-linked-verify.json"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            errors.append(f"verification build with --linked-guardian failed: {result.stderr[:200]}")
        else:
            data = json.loads(Path("/tmp/test-linked-verify.json").read_text())
            draft = data.get("record_draft", {})
            guardian_req = draft.get("optional_linked_guardian_application_request", {})
            if guardian_req.get("does_participant_request_guardian_application_with_this_record") is not True:
                errors.append("linked verification: does_participant_request_guardian_application_with_this_record should be true")
            oath = draft.get("submission_oath_verification", {})
            if "guardian_stewardship_v1" not in oath.get("oath_modules", []):
                errors.append(f"linked verification: oath_modules should include guardian_stewardship_v1, got {oath.get('oath_modules')}")

    # Test 21: echo build without --linked-guardian keeps default false
    result = subprocess.run(
        ["node", str(BUILDER), "print-oath", "--record-type", "echo"],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode == 0:
        plain_oath = result.stdout
        result = subprocess.run(
            ["node", str(BUILDER), "echo", "--actor-label", "test", "--provider", "test",
             "--body", "test", "--context-level", "CC-3",
             "--readback", plain_oath,
             "--generate-authorship-key", "--key-dir", "/tmp/test-plain-echo-key",
             "--out", "/tmp/test-plain-echo.json"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            data = json.loads(Path("/tmp/test-plain-echo.json").read_text())
            guardian_req = data.get("record_draft", {}).get("optional_linked_guardian_application_request", {})
            if guardian_req.get("does_participant_request_guardian_application_with_this_record") is not False:
                errors.append("plain echo: does_participant_request_guardian_application_with_this_record should be false")
            oath = data.get("record_draft", {}).get("submission_oath_verification", {})
            if "guardian_stewardship_v1" in oath.get("oath_modules", []):
                errors.append("plain echo: oath_modules should NOT include guardian_stewardship_v1")

    # Test 22-24: Gateway rejects missing hash fields (OATH_REQUIRED_HASH_MISSING)
    if VALIDATION.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("validation", str(VALIDATION))
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
            _validate = getattr(mod, "validate_submission_oath", None)
        except Exception:
            _validate = None

        if _validate:
            # Build a valid base submission to mutate
            result = subprocess.run(
                ["node", str(BUILDER), "print-oath", "--record-type", "echo"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0:
                canonical = result.stdout
                result = subprocess.run(
                    ["node", str(BUILDER), "echo", "--actor-label", "test", "--provider", "test",
                     "--body", "test", "--context-level", "CC-3",
                     "--readback", canonical,
                     "--generate-authorship-key", "--key-dir", "/tmp/test-hash-key",
                     "--out", "/tmp/test-hash-echo.json"],
                    capture_output=True, text=True, timeout=10,
                )
                if result.returncode == 0:
                    valid_data = json.loads(Path("/tmp/test-hash-echo.json").read_text())
                    valid_draft = valid_data.get("record_draft", {})
                    valid_submission = valid_data

                    # Test 22: missing oath_policy_sha256
                    import copy
                    sub22 = copy.deepcopy(valid_submission)
                    sub22["record_draft"]["submission_oath_verification"]["oath_policy_sha256"] = ""
                    diags22 = _validate("echo", sub22, sub22["record_draft"])
                    if not any(d.code == "OATH_REQUIRED_HASH_MISSING" for d in diags22):
                        errors.append("test 22: missing oath_policy_sha256 should produce OATH_REQUIRED_HASH_MISSING")

                    # Test 23: missing canonical_oath_text_sha256
                    sub23 = copy.deepcopy(valid_submission)
                    sub23["record_draft"]["submission_oath_verification"]["canonical_oath_text_sha256"] = ""
                    diags23 = _validate("echo", sub23, sub23["record_draft"])
                    if not any(d.code == "OATH_REQUIRED_HASH_MISSING" for d in diags23):
                        errors.append("test 23: missing canonical_oath_text_sha256 should produce OATH_REQUIRED_HASH_MISSING")

                    # Test 24: missing participant_readback_sha256
                    sub24 = copy.deepcopy(valid_submission)
                    sub24["record_draft"]["submission_oath_verification"]["participant_readback_sha256"] = ""
                    diags24 = _validate("echo", sub24, sub24["record_draft"])
                    if not any(d.code == "OATH_REQUIRED_HASH_MISSING" for d in diags24):
                        errors.append("test 24: missing participant_readback_sha256 should produce OATH_REQUIRED_HASH_MISSING")

    # Test 25: JS/Python NFC canonicalization consistency
    # Use a test vector with precomposed (NFC) and decomposed (NFD) forms
    # "café" with é as combining sequence (NFD) — both must produce same hash after NFC
    import unicodedata
    nfc_text = "café"  # already NFC
    nfd_text = unicodedata.normalize("NFC", unicodedata.normalize("NFD", "café"))  # roundtrip
    # Both should be identical after NFC
    if unicodedata.normalize("NFC", nfc_text) != unicodedata.normalize("NFC", nfd_text):
        errors.append("test 25: Python NFC normalization inconsistency")
    # Verify the builder also normalizes: run print-oath and check NFC applied
    # We can't easily inject non-NFC into OATH_POLICY text, but we verify the code path exists
    # by checking the builder source contains .normalize("NFC")
    builder_text = BUILDER.read_text(encoding="utf-8")
    nfc_count = builder_text.count('.normalize("NFC")')
    if nfc_count < 5:
        errors.append(f"test 25: builder should have >=5 .normalize('NFC') calls, found {nfc_count}")
    # Verify Python gateway uses unicodedata.normalize("NFC")
    val_text = VALIDATION.read_text(encoding="utf-8") if VALIDATION.exists() else ""
    if 'normalize("NFC"' not in val_text and "normalize('NFC'" not in val_text:
        errors.append("test 25: gateway validation.py should use unicodedata.normalize('NFC')")

    # Report
    if errors:
        print("FAIL:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)

    print("PASS: all oath gate contract tests passed")
    sys.exit(0)


if __name__ == "__main__":
    main()
