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


def main() -> None:
    text = BUILDER.read_text(encoding="utf-8")

    forbidden = [
        "test_phase_submission_may_be_reclassified",
        "test-phase submissions may be reclassified",
        "Acknowledges test-phase submissions may be reclassified",
    ]
    for phrase in forbidden:
        require(phrase not in text, f"builder still contains retired test-phase phrase: {phrase}")

    for phrase in [
        "receipt_is_intake_only",
        "later_records_may_reclassify_or_correct_this_record",
        "receipt confirms intake only",
    ]:
        require(phrase in text, f"builder missing production-live boundary phrase: {phrase}")

    manifest = json.loads(BUNDLE_MANIFEST.read_text(encoding="utf-8"))
    builder_bytes = BUILDER.read_bytes()
    require(
        manifest["canonical_builder"]["sha256"] == hashlib.sha256(builder_bytes).hexdigest(),
        "builder bundle manifest sha256 does not match builder",
    )
    require(
        manifest["canonical_builder"]["size_bytes"] == len(builder_bytes),
        "builder bundle manifest size_bytes does not match builder",
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
                "--key-dir",
                str(key_dir),
                "--out",
                str(out),
            ],
            cwd=ROOT,
        )

        generated = out.read_text(encoding="utf-8")
        require("test_phase_submission_may_be_reclassified" not in generated, "generated submission contains retired test-phase key")
        require('\"receipt_is_intake_only\":true' in generated or '\"receipt_is_intake_only\": true' in generated, "generated submission missing receipt_is_intake_only")
        require(
            "later_records_may_reclassify_or_correct_this_record" in generated,
            "generated submission missing append-only reclassification boundary",
        )

    print("Builder production-live boundary test PASSED.")


if __name__ == "__main__":
    main()
