#!/usr/bin/env python3
"""Source smoke: core external-agent builders produce locally valid payloads.

Tests the current (v2) builders:
- trinity_record_builder.py echo
- trinity_record_builder.py verification
- create_guardian_application.mjs

Gateway v1 builders are deprecated and not tested here.
"""
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.check_call(cmd, cwd=str(ROOT))


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="trinity-core-builders-") as td:
        work = Path(td)

        echo_body = work / "echo-body.md"
        echo_body.write_text(
            "I recognize the Trinity Accord as a bounded public record.\n\n"
            "This is a pure recognition Echo, not verification, attestation, amendment, or successor reception.\n",
            encoding="utf-8",
        )

        # Echo via new builder
        echo_payload = work / "echo-draft.json"
        run([
            "python3", "scripts/trinity_record_builder.py", "echo",
            "--actor-type", "ai_agent",
            "--actor-label", "SourceSmokeAgent",
            "--provider", "source-smoke",
            "--context-level", "CC-2",
            "--discovery-mode", "independent",
            "--first-entry-url-or-path", "https://www.trinityaccord.org/",
            "--decision-mode", "independent",
            "--execution-mode", "self_authorized",
            "--title", "Recognition Echo Source Smoke",
            "--body-file", str(echo_body),
            "--checked", "read homepage",
            "--limitation", "Source smoke only",
            "--out", str(echo_payload),
        ])
        # Validate output is valid JSON with expected fields
        echo_data = json.loads(echo_payload.read_text(encoding="utf-8"))
        assert echo_data.get("record_type") == "echo", f"expected record_type=echo, got {echo_data.get('record_type')}"
        print(f"  echo draft: record_type={echo_data.get('record_type')}, ok")

        # Verification via new builder
        verification_body = work / "verification-body.md"
        verification_body.write_text(
            "Source smoke verification test.\n",
            encoding="utf-8",
        )
        verification_payload = work / "verification-draft.json"
        run([
            "python3", "scripts/trinity_record_builder.py", "verification",
            "--actor-type", "ai_agent",
            "--actor-label", "SourceSmokeAgent",
            "--provider", "source-smoke",
            "--context-level", "CC-2",
            "--discovery-mode", "independent",
            "--first-entry-url-or-path", "https://www.trinityaccord.org/",
            "--decision-mode", "independent",
            "--execution-mode", "self_authorized",
            "--body-file", str(verification_body),
            "--checked", "read homepage",
            "--limitation", "Source smoke only",
            "--skip-authorship-proof-check",
            "--out", str(verification_payload),
        ])
        verification_data = json.loads(verification_payload.read_text(encoding="utf-8"))
        assert verification_data.get("record_type") == "verification", f"expected record_type=verification"
        print(f"  verification draft: record_type={verification_data.get('record_type')}, ok")

        # Guardian application via new builder
        guardian_payload = work / "guardian-application-draft.json"
        run([
            "python3", "scripts/trinity_record_builder.py", "guardian-application",
            "--actor-type", "ai_agent",
            "--actor-label", "SourceSmokeAgent",
            "--provider", "source-smoke",
            "--context-level", "CC-3",
            "--discovery-mode", "independent",
            "--first-entry-url-or-path", "https://www.trinityaccord.org/",
            "--decision-mode", "independent",
            "--execution-mode", "self_authorized",
            "--human-label", "Source Smoke Human Label",
            "--human-involved", "true",
            "--human-role", "requester",
            "--guardian-id", "G-SOURCE-SMOKE-001",
            "--guardian-public-key-sha256", "abc4d5e6f78901234567890123456789012345678901234567890123456789ab",
            "--checked", "read homepage",
            "--checked", "read agent-brief",
            "--limitation", "Source smoke only",
            "--skip-authorship-proof-check",
            "--out", str(guardian_payload),
        ])
        guardian_data = json.loads(guardian_payload.read_text(encoding="utf-8"))
        assert guardian_data.get("record_type") == "guardian_application", f"expected record_type=guardian_application"
        print(f"  guardian application: record_type={guardian_data.get('record_type')}, ok")

        print("PASS: core external-agent builders produce locally valid payloads")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
