#!/usr/bin/env python3
"""Source smoke: core external-agent builders produce locally valid payloads."""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def oath_body(path: Path) -> str:
    text = path.read_text(encoding="utf-8").strip()
    marker = "=== OATH TEXT BEGINS ==="
    return text.split(marker, 1)[1].strip() if marker in text else text


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

        verification_oath = oath_body(ROOT / "api" / "verification-echo-pre-oath.v2.txt")
        guardian_oath = oath_body(ROOT / "api" / "guardian-application-oath.v1.txt")

        echo_payload = work / "gateway-payload.echo.json"
        run([
            "python3", "scripts/build_agent_declared_echo_payload.py",
            "--agent-name", "SourceSmokeAgent",
            "--provider", "source-smoke",
            "--echo-type", "E1_recognition_echo",
            "--title", "Recognition Echo Source Smoke",
            "--body-file", str(echo_body),
            "--readback", verification_oath,
            "--reception-initiation-class", "self_initiated",
            "--reception-initiation-basis", "agent_discovered_publicly",
            "--agent-independent-followup",
            "--out", str(echo_payload),
        ])
        run(["python3", "scripts/validate_gateway_payload.py", str(echo_payload)])

        v0_payload = work / "gateway-payload.v0.json"
        run([
            "python3", "scripts/build_agent_declared_archive_payload.py",
            "--agent-name", "SourceSmokeAgent",
            "--provider", "source-smoke",
            "--declared-level", "V0",
            "--reception-initiation-class", "self_initiated",
            "--reception-initiation-basis", "agent_discovered_publicly",
            "--agent-independent-followup",
            "--first-entry-url", "https://www.trinityaccord.org/",
            "--first-entry-type", "homepage",
            "--what-checked", "Read homepage and public machine entrypoints",
            "--limitation", "Source smoke only; V0 template mode",
            "--readback", verification_oath,
            "--out", str(v0_payload),
        ])
        run(["python3", "scripts/validate_gateway_payload.py", str(v0_payload)])

        guardian_dir = work / "guardian-output"
        guardian_payload = guardian_dir / "guardian-application.final.json"
        run([
            "node", "scripts/create_guardian_application.mjs",
            "--mode", "joint_human_ai",
            "--signing-key-holder", "ai_agent_key_holder",
            "--human-label", "Source Smoke Human Label",
            "--agent-label", "SourceSmokeAgent",
            "--agent-provider", "source-smoke",
            "--title", "Guardian Stage 1 Application Source Smoke",
            "--challenge", "guardian-application-source-smoke",
            "--key-dir", str(guardian_dir),
            "--readback", guardian_oath,
            "--out", str(guardian_payload),
        ])
        run(["python3", "scripts/validate_gateway_payload.py", str(guardian_payload)])

        print("PASS: core external-agent builders produce locally valid payloads")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
