#!/usr/bin/env python3
"""Test Guardian key metadata writer."""

import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEYGEN = ROOT / "scripts" / "generate_agent_authorship_keypair.mjs"
WRITER = ROOT / "scripts" / "write_guardian_key_metadata.py"


def main():
    with tempfile.TemporaryDirectory() as td:
        prefix = Path(td) / "guardian-test-key"
        meta = Path(td) / "guardian-test-key.meta.json"

        result = subprocess.run(
            ["node", str(KEYGEN), str(prefix)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=20,
        )
        assert result.returncode == 0, result.stderr

        result = subprocess.run(
            [
                "python3", str(WRITER),
                "--public-key", str(prefix) + ".public.pem",
                "--guardian-registry-number", "00001",
                "--out", str(meta),
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=20,
        )
        assert result.returncode == 0, result.stderr

        data = json.loads(meta.read_text(encoding="utf-8"))
        assert data["schema"] == "trinityaccord.guardian-key-metadata.v1"
        assert data["guardian_registry_number"] == "00001"
        assert data["guardian_id"].startswith("guardian_ed25519_")
        assert len(data["public_key_sha256"]) == 64
        assert data["algorithm"] == "ed25519"
        assert "private" not in json.dumps(data).lower()
        assert "not authority" in data["boundary"]

    print("GUARDIAN_KEY_METADATA_OK")


if __name__ == "__main__":
    main()
