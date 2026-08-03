#!/usr/bin/env python3
"""Contract test: Guardian activation derivation.

Verifies:
1. _guardian_activation_assessment exists in trinity_record_chain.py
2. active_registered_guardian status is derivable
3. Every native Guardian entry has activation block
4. Active entries have eligible=True and empty blocking_reasons
5. Pending entries explain blocking_reasons
6. generate_guardian_current_registry.py --check passes
7. Public current registry has non-authority and receipt-not-active boundaries
8. Builder supports --guardian-id auto
9. Every manifest-pinned Builder layer has matching hash/size
10. git diff has no derived Guardian index drift after verify
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def run(cmd: list[str]) -> None:
    subprocess.check_call(cmd, cwd=ROOT)


def read_verified_builder_runtime(bundle: dict) -> str:
    canonical = bundle["canonical_builder"]
    layers = [
        (ROOT / "downloads" / "record-chain-builder.mjs", canonical),
        (
            ROOT / "downloads" / "record-chain-builder-recovery.mjs",
            canonical["recovery_wrapper"],
        ),
        (
            ROOT / "downloads" / "record-chain-builder-core.mjs",
            canonical["core"],
        ),
    ]
    texts: list[str] = []
    for path, contract in layers:
        require(path.exists(), f"missing Builder layer: {path.name}")
        raw = path.read_bytes()
        require(
            hashlib.sha256(raw).hexdigest() == contract["sha256"],
            f"Builder layer sha256 drift: {path.name}",
        )
        require(
            len(raw) == contract["size_bytes"],
            f"Builder layer size drift: {path.name}",
        )
        texts.append(raw.decode("utf-8"))
    return "\n".join(texts)


def main() -> int:
    source = (ROOT / "scripts" / "trinity_record_chain.py").read_text(encoding="utf-8")
    bundle = read_json("api/record-chain-builder-bundles.v1.json")
    builder = read_verified_builder_runtime(bundle)

    # 1. Activation helper exists
    require("_guardian_activation_assessment" in source, "missing guardian activation helper")

    # 2. active_registered_guardian derivation exists
    require("active_registered_guardian" in source, "missing active_registered_guardian derivation")

    # 3. Pending status preserved
    require("application_recorded_pending_activation" in source, "pending activation status must remain")

    # 8. Builder supports guardian-id auto across the pinned layered runtime.
    require("guardianIdForPublicKeySha" in builder, "builder must derive guardian_id from public key")
    require("isAutoGuardianId" in builder, "builder must support guardian-id auto")

    # 10. Verify and check index drift
    run([sys.executable, "scripts/trinity_record_chain.py", "verify"])

    diff = subprocess.run(
        [
            "git", "diff", "--exit-code", "--",
            "record-chain/indexes/guardian-state.json",
            "record-chain/indexes/statistics.json",
            "record-chain/indexes/guardian_application-index.json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    require(diff.returncode == 0, f"derived guardian indexes drift after verify:\n{diff.stdout}\n{diff.stderr}")

    # 3-5. Check native guardian entries
    state = read_json("record-chain/indexes/guardian-state.json")
    guardians = state.get("guardians", [])
    native = [g for g in guardians if g.get("source_record_id")]
    require(native, "expected native guardian entries")

    allowed = {
        "pending_verification",
        "application_recorded_pending_activation",
        "active_registered_guardian",
        "retired_guardian",
        "retirement_notice_unmatched",
        "retirement_pending_verification",
    }

    for g in native:
        rid = g.get("source_record_id")
        status = g.get("current_derived_status")
        require(status in allowed, f"{rid}: unexpected status {status}")
        activation = g.get("activation")
        require(isinstance(activation, dict), f"{rid}: missing activation block")
        require("eligible" in activation, f"{rid}: activation missing eligible")
        require(isinstance(activation.get("blocking_reasons"), list), f"{rid}: blocking_reasons must be list")

        if status == "active_registered_guardian":
            require(activation.get("eligible") is True, f"{rid}: active must be eligible")
            require(activation.get("blocking_reasons") == [], f"{rid}: active must have no blocking reasons")
        if status == "application_recorded_pending_activation":
            require(activation.get("eligible") is False, f"{rid}: pending must not be eligible")
            require(activation.get("blocking_reasons"), f"{rid}: pending must explain why")

    # 6. Generator --check passes
    run([sys.executable, "scripts/generate_guardian_current_registry.py"])
    run([sys.executable, "scripts/generate_guardian_current_registry.py", "--check"])

    # 7. Public registry boundaries
    current = read_json("api/guardian-current-registry.json")
    require(current.get("schema") == "trinityaccord.guardian-current-registry.v1", "current registry schema mismatch")
    boundary = current.get("boundary", {})
    for key in [
        "not_authority",
        "not_governance",
        "not_attestation",
        "not_verification_level",
        "not_successor_reception",
        "not_amendment",
        "bitcoin_originals_prevail",
        "receipt_is_not_active_guardian_status",
    ]:
        require(boundary.get(key) is True, f"current registry boundary missing {key}")

    print("Guardian activation derivation contract PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
