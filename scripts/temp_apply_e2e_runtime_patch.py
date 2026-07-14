#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one anchor, found {count}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


# Builder: guardian-retirement --guardian-id auto must derive the same ID as application.
replace_once(
    "downloads/record-chain-builder.mjs",
    '''    recordDraft.guardian_public_key_sha256 = pubSha;
  }

  const linked = recordDraft.optional_linked_guardian_application_request;''',
    '''    recordDraft.guardian_public_key_sha256 = pubSha;

    const derivedGuardianId = guardianIdForPublicKeySha(pubSha);
    const requestedGuardianId = String(recordDraft.guardian_id || "").trim();
    if (!requestedGuardianId || isAutoGuardianId(requestedGuardianId)) {
      recordDraft.guardian_id = derivedGuardianId;
    } else if (requestedGuardianId !== derivedGuardianId) {
      errorExit("--guardian-id must equal guardian_ed25519_<first16-of-authorship-public-key-sha256>; use --guardian-id auto");
    }
  }

  const linked = recordDraft.optional_linked_guardian_application_request;''',
)

# Gateway: corrections are author-only; third-party review is classification_update.
p = Path("apps/record_chain_intake_gateway/app.py")
text = p.read_text(encoding="utf-8")
start = text.index("async def _record_target_diagnostics")
end = text.index("\n\ndef _build_agent_recovery", start)
block = text[start:end]
marker = "    return diagnostics\n"
pos = block.rfind(marker)
if pos < 0:
    raise SystemExit("record target return marker not found")
insertion = '''    if record_type == "correction" and isinstance(target, dict):
        current_proof = body.get("authorship_proof") or body.get("proof") or draft.get("authorship_proof")
        target_proof = target.get("authorship_proof")
        current_key = current_proof.get("public_key_sha256") if isinstance(current_proof, dict) else None
        target_key = target_proof.get("public_key_sha256") if isinstance(target_proof, dict) else None
        if not isinstance(target_key, str) or not re.fullmatch(r"[a-f0-9]{64}", target_key):
            diagnostics.append(Diagnostic(
                code="CORRECTION_TARGET_AUTHORSHIP_UNAVAILABLE", severity="error",
                field=f"{field_prefix}.target_record_id",
                message=f"Target record {target_id} has no verifiable Ed25519 authorship key.",
                meaning="Correction is author-only; unsigned legacy targets require classification_update.",
                suggested_fix="Use classification_update, or use the original key for a current signed target.",
                retry_allowed=False,
            ))
        elif current_key != target_key:
            diagnostics.append(Diagnostic(
                code="CORRECTION_TARGET_AUTHOR_MISMATCH", severity="error",
                field="authorship_proof.public_key_sha256",
                message=f"Correction signer does not match target record {target_id} author key.",
                meaning="The correction oath applies only to a prior record authored by this signer.",
                suggested_fix="Use the target author's key, or submit classification_update instead.",
                retry_allowed=False,
            ))
'''
block = block[:pos] + insertion + block[pos:]
p.write_text(text[:start] + block + text[end:], encoding="utf-8")

# Append defense in depth.
replace_once(
    "scripts/trinity_record_chain.py",
    '''    if target.get("record_sha256") != target_sha:
        raise ValueError(f"{record_type} target_record_sha256 mismatch for {target_id}")
''',
    '''    if target.get("record_sha256") != target_sha:
        raise ValueError(f"{record_type} target_record_sha256 mismatch for {target_id}")
    if record_type == "correction":
        current_proof = draft.get("authorship_proof")
        target_proof = target.get("authorship_proof")
        current_key = current_proof.get("public_key_sha256") if isinstance(current_proof, dict) else None
        target_key = target_proof.get("public_key_sha256") if isinstance(target_proof, dict) else None
        if not isinstance(target_key, str) or not _HEX64_RE.fullmatch(target_key):
            raise ValueError(f"correction target {target_id} has no verifiable authorship key; use classification_update")
        if current_key != target_key:
            raise ValueError(f"correction signer key does not match target record author key for {target_id}")
''',
)

# Retired verification wording.
replace_once(
    "apps/record_chain_intake_gateway/gateway/validation.py",
    "Public Record-Chain verification intake currently accepts only V0-V5. V6+ strict evidence is reserved for a future/internal route.",
    "Public Record-Chain verification intake accepts V0-V5 only as legacy compatibility metadata. V4+, V6, V7, and V8 are historical-only; use digital_profile, physical_observation, and external_witness.",
)

# Agent guidance and diagnostics.
p = Path("downloads/record-chain-agent-field-guidance.v1.json")
data = json.loads(p.read_text(encoding="utf-8"))
c = data["record_types"]["correction"]
c.setdefault("not_for", [])
for value in ["correcting a record authored by another Ed25519 key", "third-party review; use classification_update"]:
    if value not in c["not_for"]:
        c["not_for"].append(value)
note = "Confirm the current authorship key equals the target final record authorship_proof key."
if note not in c["before_build"]:
    c["before_build"].insert(1, note)
c["author_binding_rule"] = "Correction is author-only; signer public_key_sha256 must equal the target author key."
c["third_party_route"] = "Use classification_update for third-party critique or reclassification."
data["record_types"]["classification_update"]["third_party_role"] = "Bounded third-party assessment; does not mutate the target record."
p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

p = Path("api/record-chain-field-helper.v1.json")
data = json.loads(p.read_text(encoding="utf-8"))
advice = data["agent_recovery_protocol"]["what_not_to_fake"]
data["agent_recovery_protocol"]["what_not_to_fake"] = [
    "Do not use retired V4+, V6, V7, or V8 labels for new public verification submissions."
    if item == "Do not claim V6+ verification without running the required scripts." else item
    for item in advice
]
data["diagnostic_code_help"]["CORRECTION_TARGET_AUTHORSHIP_UNAVAILABLE"] = {
    "meaning": "Target lacks a verifiable Ed25519 author key; author-only correction cannot be bound.",
    "fix": "Use classification_update, or target a current signed record with its original key.",
    "recovery_possible": False, "severity": "error",
}
data["diagnostic_code_help"]["CORRECTION_TARGET_AUTHOR_MISMATCH"] = {
    "meaning": "Correction signer differs from the immutable target record author.",
    "fix": "Use the original author key, or submit classification_update for third-party review.",
    "recovery_possible": False, "severity": "error",
}
p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
