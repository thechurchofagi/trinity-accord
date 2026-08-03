#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "downloads" / "record-chain-builder.mjs"
BUNDLE_MANIFEST = ROOT / "api" / "record-chain-builder-bundles.v1.json"


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def _load_verified_runtime_sources(manifest: dict) -> str:
    """Load every manifest-pinned Builder layer for source-contract checks."""
    canonical = manifest["canonical_builder"]
    layers = [
        (BUILDER, canonical),
        (
            ROOT / "downloads" / "record-chain-builder-recovery.mjs",
            canonical["recovery_wrapper"],
        ),
        (
            ROOT / "downloads" / "record-chain-builder-core.mjs",
            canonical["core"],
        ),
    ]
    source_texts: list[str] = []
    for path, contract in layers:
        raw = path.read_bytes()
        require(
            hashlib.sha256(raw).hexdigest() == contract["sha256"],
            f"Builder layer manifest sha256 does not match {path.name}",
        )
        require(
            len(raw) == contract["size_bytes"],
            f"Builder layer manifest size_bytes does not match {path.name}",
        )
        source_texts.append(raw.decode("utf-8"))
    return "\n".join(source_texts)


def main() -> None:
    manifest = json.loads(BUNDLE_MANIFEST.read_text(encoding="utf-8"))
    runtime_text = _load_verified_runtime_sources(manifest)

    forbidden = [
        "test_phase_submission_may_be_reclassified",
        "test-phase submissions may be reclassified",
        "Acknowledges test-phase submissions may be reclassified",
    ]
    for phrase in forbidden:
        require(
            phrase not in runtime_text,
            f"Builder runtime still contains retired test-phase phrase: {phrase}",
        )

    for phrase in [
        "receipt_is_intake_only",
        "later_records_may_reclassify_or_correct_this_record",
        "receipt confirms intake only",
    ]:
        require(
            phrase in runtime_text,
            f"Builder runtime missing production-live boundary phrase: {phrase}",
        )

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "echo.json"
        key_dir = Path(td) / "keys"
        oath = subprocess.check_output(
            ["node", str(BUILDER), "print-oath", "--record-type", "echo"],
            cwd=ROOT,
            text=True,
        )

        subprocess.check_call(
            [
                "node",
                str(BUILDER),
                "echo",
                "--actor-label",
                "Builder Production Boundary Test Agent",
                "--provider",
                "local",
                "--body",
                "Production-live builder boundary smoke.",
                "--context-level",
                "CC-3",
                "--context-read-confirmed",
                "true",
                "--context-sufficient-for-selected-action",
                "true",
                "--loaded-urls",
                "https://www.trinityaccord.org/agent-start/",
                "--discovery-mode",
                "self_discovered",
                "--record-decision",
                "self",
                "--submission-executor",
                "self",
                "--requesting-party-type",
                "none",
                "--introducing-party-type",
                "none",
                "--human-operator-involved",
                "false",
                "--readback",
                oath,
                "--contextual-readback-confirmed",
                "true",
                "--key-dir",
                str(key_dir),
                "--out",
                str(out),
            ],
            cwd=ROOT,
        )

        generated = out.read_text(encoding="utf-8")
        require(
            "test_phase_submission_may_be_reclassified" not in generated,
            "generated submission contains retired test-phase key",
        )
        require(
            '\"receipt_is_intake_only\":true' in generated
            or '\"receipt_is_intake_only\": true' in generated,
            "generated submission missing receipt_is_intake_only",
        )
        require(
            "later_records_may_reclassify_or_correct_this_record" in generated,
            "generated submission missing append-only reclassification boundary",
        )

    print("Builder production-live boundary test PASSED.")


if __name__ == "__main__":
    main()
