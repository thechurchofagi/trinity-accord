#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "downloads/record-chain-builder.mjs"


def run(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    if check and result.returncode != 0:
        raise AssertionError(f"command failed: {' '.join(args)}\nstdout={result.stdout}\nstderr={result.stderr}")
    return result


def main() -> int:
    oath = run(["node", str(BUILDER), "print-oath", "--record-type", "verification"]).stdout.strip()
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        out = temp / "verification.json"
        key_dir = temp / "keys"
        command = [
            "node", str(BUILDER), "verification",
            "--actor-label", "Migration Test Agent",
            "--provider", "CI",
            "--verification-level", "V3",
            "--scope-label", "legacy V3 compatibility",
            "--what-was-checked", "manifest bytes,mirror bytes",
            "--verification-claim", "The declared test bytes match the expected test digest.",
            "--fresh-actions", "read manifest,computed hash,compared result",
            "--digital-profile", "integrity_checked",
            "--relationships-checked", "hashes,mirrors_bytes",
            "--physical-observation", "none",
            "--external-witness", "none",
            "--coverage-scope", "single_target",
            "--limitations", "test fixture only,not full public coverage",
            "--claims-not-made", "semantic truth,institutional endorsement,physical identity",
            "--corrections-or-supersession-checked", "true",
            "--action-profile", "verification",
            "--context-level", "CC-3",
            "--context-sufficient-for-selected-action", "true",
            "--context-read-confirmed", "true",
            "--loaded-urls", "https://www.trinityaccord.org/api/verification-claim-model.v1.json,https://www.trinityaccord.org/api/evidence-relationship-map.v1.json",
            "--discovery-mode", "user_task_context",
            "--requesting-party-type", "human",
            "--introducing-party-type", "human",
            "--record-decision", "mixed",
            "--submission-executor", "self",
            "--human-operator-involved", "false",
            "--readback", oath,
            "--key-dir", str(key_dir),
            "--out", str(out),
        ]
        run(command)
        submission = json.loads(out.read_text(encoding="utf-8"))
        draft = submission["record_draft"]
        readiness = draft["context_readiness"]
        assert readiness["action_profile"] == "verification"
        assert readiness["legacy_cc_level_role"] == "builder_compatibility_only"
        assert readiness["interpretation_model_policy"] == "/api/interpretation-model-policy.v1.json"
        model = draft["verification_content"]["verification_claim_model"]
        assert model["schema"] == "trinityaccord.verification-claim-model.v1"
        assert model["digital_profile"] == "integrity_checked"
        assert model["relationships_checked"] == ["hashes", "mirrors_bytes"]
        assert model["physical_observation"] == "none"
        assert model["external_witness"] == "none"
        assert model["coverage_scope"] == "single_target"
        assert model["corrections_or_supersession_checked"] is True
        assert model["legacy_v_level"] == "V3"
        assert model["legacy_v_level_role"] == "builder_compatibility_only"
        run(["node", str(BUILDER), "doctor", "--file", str(out)])

        rejected = command.copy()
        rejected[rejected.index("V3")] = "V8"
        rejected[rejected.index(str(out))] = str(temp / "rejected.json")
        result = run(rejected, check=False)
        assert result.returncode != 0
        assert "historical-only" in result.stderr

    print("BUILDER_MULTIDIMENSIONAL_VERIFICATION_OK")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"BUILDER_MULTIDIMENSIONAL_VERIFICATION_FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
