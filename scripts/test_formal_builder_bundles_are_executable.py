#!/usr/bin/env python3
"""Exported zero-clone bundles must be executable after extraction."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BUNDLES = {
    "trinity-pure-echo-builder-bundle.tar.gz": [
        ["python3", "scripts/build_agent_declared_echo_payload.py", "--help"],
        ["python3", "scripts/build_agent_declared_echo_payload.py", "--print-oath"],
    ],
    "trinity-v0v5-builder-bundle.tar.gz": [
        ["python3", "scripts/build_agent_declared_archive_payload.py", "--help"],
        ["python3", "scripts/build_agent_declared_archive_payload.py", "--print-oath"],
    ],
    "trinity-guardian-stage1-builder-bundle.tar.gz": [
        ["node", "scripts/create_guardian_application.mjs", "--print-oath"],
        ["node", "scripts/create_guardian_application.mjs", "--explain"],
    ],
    "trinity-guardian-stage2-builder-bundle.tar.gz": [
        ["python3", "scripts/build_guardian_listing_request_payload.py", "--help"],
    ],
    "trinity-guardian-signed-echo-builder-bundle.tar.gz": [
        ["python3", "scripts/build_guardian_echo_payload.py", "--help"],
        ["python3", "scripts/build_agent_declared_echo_payload.py", "--help"],
    ],
}

def safe_extract(archive: Path, dest: Path) -> None:
    with tarfile.open(archive, "r:gz") as tar:
        for member in tar.getmembers():
            target = (dest / member.name).resolve()
            root = dest.resolve()
            if not str(target).startswith(str(root) + os.sep):
                raise RuntimeError(f"unsafe tar path: {member.name}")
        tar.extractall(dest)

def run(cmd: list[str], cwd: Path) -> None:
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        print(f"FAIL: command failed in extracted bundle: {' '.join(cmd)}")
        print("--- stdout ---")
        print(result.stdout)
        print("--- stderr ---")
        print(result.stderr)
        raise SystemExit(1)

def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "bundles"
        subprocess.check_call([
            "python3",
            str(ROOT / "scripts" / "export_formal_builder_bundles.py"),
            "--out-dir",
            str(out),
        ])

        for archive_name, commands in BUNDLES.items():
            archive = out / archive_name
            if not archive.exists():
                print(f"FAIL: archive missing after export: {archive_name}")
                return 1

            extract_dir = Path(td) / ("extract-" + archive_name.replace(".tar.gz", ""))
            extract_dir.mkdir()
            safe_extract(archive, extract_dir)

            for cmd in commands:
                run(cmd, extract_dir)

    print("PASS: exported zero-clone bundles are executable after extraction")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
