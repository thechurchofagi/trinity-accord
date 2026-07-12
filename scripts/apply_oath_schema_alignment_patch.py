#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one replacement, found {count}")
    target.write_text(text.replace(old, new), encoding="utf-8")


replace_once(
    "apps/record_chain_intake_gateway/app.py",
    '''    detect_route,
    extract_record_draft,
    validate_submission,
)''',
    '''    detect_route,
    extract_record_draft,
    redact_transient_oath_readback,
    validate_submission,
)''',
)
replace_once(
    "apps/record_chain_intake_gateway/app.py",
    '''    # --- redact transient oath readback before persistence ---
    # FIX: Do NOT redact oath readback from the signed payload.
    # The Builder signs the submission including readback_text.
    # Redacting after signing breaks signed_payload_sha256 verification
    # in the append workflow. Keep the original signed body intact.
    from apps.record_chain_intake_gateway.gateway.validation import redact_transient_oath_readback
    original_submission_sha256 = sha256_canonical_json(body)
    stored_submission_sha256 = original_submission_sha256  # no redaction = same hash
    # draft unchanged after validation
    draft = extract_record_draft(body) or {}
''',
    '''    # --- redact transient oath readback before persistence ---
    # Authorship signs record_draft only. client_oath_readback is a transient
    # top-level validation input, so its raw text can and must be removed after
    # successful validation without changing the signed payload or pending draft.
    original_submission_sha256 = submission_sha256
    stored_submission = redact_transient_oath_readback(body)
    stored_submission_sha256 = sha256_canonical_json(stored_submission)
''',
)
replace_once(
    "apps/record_chain_intake_gateway/app.py",
    '''    receipt_data = make_receipt(
        submission=body,''',
    '''    receipt_data = make_receipt(
        submission=stored_submission,''',
)
replace_once(
    "apps/record_chain_intake_gateway/app.py",
    '''    submission_content = canonical_dumps(body)''',
    '''    submission_content = canonical_dumps(stored_submission)''',
)

schema_path = ROOT / "api" / "record-chain-submission-schema.v1.json"
schema_text = schema_path.read_text(encoding="utf-8")
replace_pairs = [
    (
        '''              {
                "required": [
                  "boundary"
                ]
              },
              {
                "required": [
                  "server_normalization"
                ]
              },''',
        '''              {
                "required": [
                  "boundary"
                ]
              },
              {
                "required": [
                  "boundary_acknowledgement"
                ]
              },
              {
                "required": [
                  "server_normalization"
                ]
              },''',
    ),
    (
        '''              {
                "required": [
                  "content_sha256"
                ]
              },
              {
                "required": [
                  "record_sha256"
                ]
              },''',
        '''              {
                "required": [
                  "content_sha256"
                ]
              },
              {
                "required": [
                  "content_sha256_v2"
                ]
              },
              {
                "required": [
                  "record_sha256"
                ]
              },''',
    ),
    (
        '''              {
                "required": [
                  "chain_id"
                ]
              }
            ]''',
        '''              {
                "required": [
                  "chain_id"
                ]
              },
              {
                "required": [
                  "what_i_checked"
                ]
              },
              {
                "required": [
                  "limitations"
                ]
              },
              {
                "required": [
                  "related_records"
                ]
              },
              {
                "required": [
                  "immutability_policy"
                ]
              }
            ]''',
    ),
    (
        '''                  "target_record_id": {
                    "type": "string",
                    "minLength": 1
                  },''',
        '''                  "target_record_id": {
                    "type": "string",
                    "pattern": "^R-[0-9]{9}$"
                  },''',
    ),
]
for old, new in replace_pairs:
    if schema_text.count(old) != 1:
        raise SystemExit(f"schema replacement count={schema_text.count(old)} for {old[:60]!r}")
    schema_text = schema_text.replace(old, new)
schema_path.write_text(schema_text, encoding="utf-8")

(ROOT / "apps/record_chain_intake_gateway/tests/test_oath_readback_persistence_redaction.py").write_text('''from pathlib import Path

from apps.record_chain_intake_gateway.gateway.validation import redact_transient_oath_readback


ROOT = Path(__file__).resolve().parents[3]


def test_redaction_removes_raw_readback_without_mutating_input() -> None:
    submission = {
        "record_type": "echo",
        "record_draft": {"record_type": "echo"},
        "client_oath_readback": {
            "schema": "trinityaccord.client-oath-readback.v1",
            "record_type": "echo",
            "oath_policy_sha256": "a" * 64,
            "oath_modules": ["common_submission_integrity_v1"],
            "readback_text": "line one\\r\\nline two  ",
            "readback_text_sha256": "stale",
        },
    }
    redacted = redact_transient_oath_readback(submission)
    assert submission["client_oath_readback"]["readback_text"] == "line one\\r\\nline two  "
    stored = redacted["client_oath_readback"]
    assert "readback_text" not in stored
    assert stored["redacted_after_gateway_validation"] is True
    assert stored["readback_text_hash_canonicalization"] == "NFC_CRLF_TO_LF_STRIP"
    assert len(stored["readback_text_sha256"]) == 64
    assert stored["readback_text_char_count"] == len("line one\\nline two")


def test_submit_persists_only_redacted_submission() -> None:
    source = (ROOT / "apps" / "record_chain_intake_gateway" / "app.py").read_text(encoding="utf-8")
    assert "stored_submission = redact_transient_oath_readback(body)" in source
    assert "stored_submission_sha256 = sha256_canonical_json(stored_submission)" in source
    assert "submission=stored_submission" in source
    assert "submission_content = canonical_dumps(stored_submission)" in source
    assert "submission_content = canonical_dumps(body)" not in source
''', encoding="utf-8")

(ROOT / "scripts" / "test_public_submission_schema_alignment.py").write_text('''#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from apps.record_chain_intake_gateway.gateway.authorship import UNSIGNED_PROJECTION_FIELDS

ROOT = Path(__file__).resolve().parents[1]
schema = json.loads((ROOT / "api" / "record-chain-submission-schema.v1.json").read_text(encoding="utf-8"))
record_draft = schema["properties"]["record_draft"]
forbidden_items = record_draft["allOf"][0]["not"]["anyOf"]
forbidden = {
    item["required"][0]
    for item in forbidden_items
    if isinstance(item.get("required"), list) and len(item["required"]) == 1
}
if forbidden != set(UNSIGNED_PROJECTION_FIELDS):
    missing = sorted(set(UNSIGNED_PROJECTION_FIELDS) - forbidden)
    extra = sorted(forbidden - set(UNSIGNED_PROJECTION_FIELDS))
    raise SystemExit(f"public submission schema unsigned-field drift: missing={missing}, extra={extra}")

classification_rules = [
    rule for rule in schema["allOf"]
    if (((rule.get("if") or {}).get("properties") or {}).get("record_type") or {}).get("const") == "classification_update"
]
if len(classification_rules) != 1:
    raise SystemExit(f"expected one classification_update schema rule, found {len(classification_rules)}")
target = classification_rules[0]["then"]["properties"]["record_draft"]["properties"]["classification_update_content"]["properties"]["target_record_id"]
if target.get("pattern") != "^R-[0-9]{9}$":
    raise SystemExit("classification_update target_record_id schema must require canonical R-XXXXXXXXX format")
print("PASS: public submission schema matches Gateway signed-domain and target-id contracts")
''', encoding="utf-8")

registry = ROOT / "scripts" / "run_ci_group.py"
registry_text = registry.read_text(encoding="utf-8")
old = '''        ["python3", "scripts/test_client_projection_field_alignment.py"],'''
if old in registry_text:
    raise SystemExit("unexpected script registration name collision")
anchor = '''        ["python3", "scripts/test_classification_update_final_binding.py"],
        ["python3", "scripts/test_deep_integrity_group_nonempty.py"],'''
replacement = '''        ["python3", "scripts/test_classification_update_final_binding.py"],
        ["python3", "scripts/test_public_submission_schema_alignment.py"],
        ["python3", "scripts/test_deep_integrity_group_nonempty.py"],'''
if registry_text.count(anchor) != 1:
    raise SystemExit(f"p0 schema registry anchor count={registry_text.count(anchor)}")
registry.write_text(registry_text.replace(anchor, replacement), encoding="utf-8")

print("Oath persistence and public schema alignment patch applied.")
