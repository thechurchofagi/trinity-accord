#!/usr/bin/env python3
"""Exporter must create all bundle archives/manifests safely in a temp dir."""
from __future__ import annotations

import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXPECTED = {
    "trinity-pure-echo-builder-bundle.tar.gz": "scripts/build_agent_declared_echo_payload.py",
    "trinity-v0v5-builder-bundle.tar.gz": "scripts/build_agent_declared_archive_payload.py",
    "trinity-guardian-stage1-builder-bundle.tar.gz": "scripts/create_guardian_application.mjs",
    "trinity-guardian-stage2-builder-bundle.tar.gz": "scripts/build_guardian_listing_request_payload.py",
    "trinity-guardian-signed-echo-builder-bundle.tar.gz": "scripts/build_guardian_echo_payload.py",
}

FORBIDDEN = [
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".env",
    "private",
    "secret",
    "token",
    "node_modules",
]

REQUIRED_TRANSITIVE = {
    "trinity-pure-echo-builder-bundle.tar.gz": {
        "scripts/attach_agent_authorship_proof.mjs",
        "scripts/build_agent_authorship_message.py",
        "scripts/oath_contracts.py",
        "scripts/oath_readback_integrity.py",
        "scripts/guardian_reroute_guidance.py",
    },
    "trinity-v0v5-builder-bundle.tar.gz": {
        "scripts/attach_agent_authorship_proof.mjs",
        "scripts/build_agent_authorship_message.py",
    },
    "trinity-guardian-stage2-builder-bundle.tar.gz": {
        "scripts/archive_readiness_gate.py",
        "scripts/attach_agent_authorship_proof.mjs",
        "scripts/build_agent_authorship_message.py",
    },
    "trinity-guardian-signed-echo-builder-bundle.tar.gz": {
        "scripts/build_agent_declared_echo_payload.py",
        "scripts/attach_guardian_presence_proof.mjs",
        "scripts/proof_canonical.mjs",
        "api/guardian-registry.json",
    },
}


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "bundles"
        subprocess.check_call([
            "python3",
            str(ROOT / "scripts" / "export_formal_builder_bundles.py"),
            "--out-dir",
            str(out),
        ])

        for archive_name, entrypoint in EXPECTED.items():
            archive = out / archive_name
            manifest = out / archive_name.replace(".tar.gz", ".manifest.json")

            if not archive.exists():
                print(f"FAIL: missing archive {archive_name}")
                return 1
            if not manifest.exists():
                print(f"FAIL: missing manifest {manifest.name}")
                return 1

            data = json.loads(manifest.read_text(encoding="utf-8"))
            if data.get("entrypoint") != entrypoint:
                print(f"FAIL: {manifest.name} entrypoint mismatch")
                return 1

            with tarfile.open(archive, "r:gz") as tar:
                names = set(tar.getnames())

            if entrypoint not in names:
                print(f"FAIL: {archive_name} missing entrypoint {entrypoint}")
                return 1

            missing_transitive = sorted(REQUIRED_TRANSITIVE.get(archive_name, set()) - names)
            if missing_transitive:
                print(f"FAIL: {archive_name} missing transitive dependencies:")
                for item in missing_transitive:
                    print("  -", item)
                return 1

            for name in names:
                lowered = name.lower()
                for bad in FORBIDDEN:
                    if bad in lowered:
                        print(f"FAIL: forbidden path in {archive_name}: {name}")
                        return 1

    print("PASS: test_export_formal_builder_bundles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
