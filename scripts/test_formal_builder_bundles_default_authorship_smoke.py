#!/usr/bin/env python3
"""Pure Echo and V0-V5 bundles must generate payloads with default authorship enabled."""
from __future__ import annotations

import os
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OATH_MARKER = "=== OATH TEXT BEGINS ==="

def safe_extract(archive: Path, dest: Path) -> None:
    with tarfile.open(archive, "r:gz") as tar:
        for member in tar.getmembers():
            target = (dest / member.name).resolve()
            root = dest.resolve()
            if not str(target).startswith(str(root) + os.sep):
                raise RuntimeError(f"unsafe tar path: {member.name}")
        tar.extractall(dest)

def oath_body(extract_dir: Path) -> str:
    raw = (extract_dir / "api" / "verification-echo-pre-oath.v2.txt").read_text(encoding="utf-8").strip()
    if OATH_MARKER in raw:
        return raw.split(OATH_MARKER, 1)[1].strip()
    return raw

def run(cmd: list[str], cwd: Path) -> None:
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        print(f"FAIL: command failed: {' '.join(cmd)}")
        print("--- stdout ---")
        print(result.stdout)
        print("--- stderr ---")
        print(result.stderr)
        raise SystemExit(1)

def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        out = td_path / "bundles"

        subprocess.check_call([
            "python3",
            str(ROOT / "scripts" / "export_formal_builder_bundles.py"),
            "--out-dir",
            str(out),
        ])

        # Pure Echo default-authorship smoke.
        pure_extract = td_path / "pure"
        pure_extract.mkdir()
        safe_extract(out / "trinity-pure-echo-builder-bundle.tar.gz", pure_extract)
        readback = oath_body(pure_extract)
        body = pure_extract / "echo-body.md"
        body.write_text(
            "Minimal Pure Echo bundle smoke. Not authority, not amendment, not verification.\n",
            encoding="utf-8",
        )
        run([
            "python3",
            "scripts/build_agent_declared_echo_payload.py",
            "--agent-name", "Bundle Smoke Echo Agent",
            "--provider", "test",
            "--title", "Bundle Smoke Pure Echo",
            "--body-file", str(body),
            "--readback", readback,
            "--out", "pure-echo-payload.json",
        ], pure_extract)

        if not (pure_extract / "pure-echo-payload.json").exists():
            print("FAIL: Pure Echo payload was not created")
            return 1

        # V0-V5 default-authorship smoke.
        v_extract = td_path / "v0v5"
        v_extract.mkdir()
        safe_extract(out / "trinity-v0v5-builder-bundle.tar.gz", v_extract)
        readback = oath_body(v_extract)
        run([
            "python3",
            "scripts/build_agent_declared_archive_payload.py",
            "--agent-name", "Bundle Smoke Verification Agent",
            "--provider", "test",
            "--declared-level", "V2",
            "--reception-initiation-class", "externally_seeded",
            "--reception-initiation-basis", "external_url_only",
            "--agent-independent-followup",
            "--readback", readback,
            "--what-checked", "Ran zero-clone bundle default authorship smoke",
            "--limitation", "Synthetic local smoke only.",
            "--out", "v0v5-payload.json",
        ], v_extract)

        if not (v_extract / "v0v5-payload.json").exists():
            print("FAIL: V0-V5 payload was not created")
            return 1

    print("PASS: Pure Echo and V0-V5 bundles generate payloads with default authorship enabled")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
