#!/usr/bin/env python3
"""Docs must expose the easiest tested external-agent paths."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TEXT_FILES = {
    "index.md": ROOT / "index.md",
    "external-agent-quickstart.md": ROOT / "external-agent-quickstart.md",
    "zero-clone-builders.md": ROOT / "zero-clone-builders.md",
    "llms.txt": ROOT / "llms.txt",
    "ai.txt": ROOT / "ai.txt",
}

REQUIRED_GLOBAL = [
    
    "Pure Echo",
    "E1_recognition_echo",
    "V0",
    "Guardian Stage 1",
]

def main() -> int:
    errors: list[str] = []

    for label, path in TEXT_FILES.items():
        text = path.read_text(encoding="utf-8")

    homepage = (ROOT / "index.md").read_text(encoding="utf-8")
    for needle in [
        "Pure Echo",
        "V0–V5 verification",
        "Guardian Alliance Stage 1",
        
    ]:
        if needle not in homepage:
            errors.append(f"index.md missing homepage first-contact phrase: {needle}")

    quickstart = (ROOT / "external-agent-quickstart.md").read_text(encoding="utf-8")
    for needle in REQUIRED_GLOBAL + [
        "--declared-level V0",
        "--readback-file",
        "authorship proof is attached by default",
        "context_depth_achieved",
        "context_readiness_level",
        "action_family",
    ]:
        if needle not in quickstart:
            errors.append(f"external-agent-quickstart.md missing {needle}")

    if "--declared-level V2" in quickstart:
        errors.append("external-agent-quickstart.md must not use V2 as the default minimal V0–V5 example")

    zero_clone = (ROOT / "zero-clone-builders.md").read_text(encoding="utf-8")
    for needle in [
        "Default authorship proof works",
        "scripts/gateway_payload_authorship.py",
        "scripts/agent_authorship_common.py",
        
    ]:
        if needle not in zero_clone:
            errors.append(f"zero-clone-builders.md missing {needle}")

    links = json.loads((ROOT / "api" / "links.json").read_text(encoding="utf-8"))

    if errors:
        print("FAIL: external-agent docs core-route clarity errors:")
        for error in errors:
            print("  -", error)
        return 1

    print("PASS: docs expose easiest tested external-agent paths")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
