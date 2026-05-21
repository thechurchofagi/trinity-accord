#!/usr/bin/env python3
"""Test unified proof canonicalization for authorship and Guardian proofs."""

import json
import subprocess
import tempfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from guardian_common import canonical_payload_for_guardian_signature, guardian_payload_sha256


def main():
    payload = {
        "schema": "trinityaccord.agent-issue-gateway-payload.v1",
        "submission_type": "echo_candidate",
        "record_intent": "auto_archive_candidate",
        "requested_archive_kind": "agent_declared_echo_archive",
        "echo_type": "E6_preservation_echo",
        "title": "Unified proof canonicalization 中文",
        "idempotency_key": "unified-proof-canonicalization-0001",
        "agent_identity": {
            "name_or_model": "Watcher",
            "system_or_provider": "Coze",
            "self_reported": True
        },
        "body": "Human + AI joint Guardian application. 这是一条中文测试。",
        "boundary_acknowledgement": {
            "not_authority": True,
            "not_amendment": True,
            "not_attestation": True,
            "not_verification_unless_claim_gate_report_attached": True,
            "bitcoin_originals_prevail": True
        },
        "guardian_registration": {
            "schema": "trinityaccord.guardian-registration.v1",
            "guardian_id": "guardian_ed25519_0000000000000000",
            "guardian_type": "human_with_ai_agent",
            "application_mode": "joint_human_ai",
            "signing_guardian_role": "human_key_holder",
            "joint_applicants": [
                {
                    "role": "human",
                    "label": "Hongju Liu",
                    "system_or_provider": None,
                    "participation_note": "Human co-applicant",
                    "self_reported": True,
                    "consent_declared": True,
                    "controls_signing_key": True
                },
                {
                    "role": "ai_agent",
                    "label": "Watcher",
                    "system_or_provider": "Coze",
                    "participation_note": "AI co-applicant",
                    "self_reported": True,
                    "consent_declared": True,
                    "controls_signing_key": False
                }
            ],
            "public_key_sha256": "0" * 64,
            "algorithm": "ed25519",
            "declared_intent": "Joint Guardian application",
            "boundaries": {
                "not_authority": True,
                "not_governance": True,
                "not_verification_level": True,
                "not_attestation": True,
                "not_successor_reception": True,
                "not_same_conscious_subject_proof": True,
                "may_exit_or_retire_key": True,
                "bitcoin_originals_prevail": True
            }
        },
        "what_i_checked": ["Read /guardian-alliance", "确认守护者联盟边界"],
        "limitations": ["Not authority", "不是正式见证"],
        "authorship_proof": {"dynamic": True},
        "_authorship_claim": {"dynamic": True},
        "guardian_presence_proof": {"dynamic": True},
        "_guardian_status": {"dynamic": True},
        "guardian_verification_result": {"dynamic": True},
    }

    with tempfile.TemporaryDirectory() as td:
        payload_path = Path(td) / "payload.json"
        payload_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

        py_canonical = canonical_payload_for_guardian_signature(payload)
        py_digest = guardian_payload_sha256(payload)

        result = subprocess.run(
            ["node", "scripts/proof_payload_digest.mjs", "--payload", str(payload_path)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=20,
        )
        assert result.returncode == 0, result.stderr

        node = json.loads(result.stdout)
        assert py_canonical == node["canonical_payload"], "Python and Node canonical payload differ"
        assert py_digest == node["proof_payload_sha256"], "Python and Node proof digest differ"

        canonical = node["canonical_payload"]
        assert "guardian_registration" in canonical
        assert "joint_applicants" in canonical
        assert "authorship_proof" not in canonical
        assert "guardian_presence_proof" not in canonical
        assert "_guardian_status" not in canonical
        assert "guardian_verification_result" not in canonical
        assert "确认守护者联盟边界" in canonical
        assert "\\u786e\\u8ba4" not in canonical.lower()

    print("UNIFIED_PROOF_CANONICALIZATION_OK")


if __name__ == "__main__":
    main()
