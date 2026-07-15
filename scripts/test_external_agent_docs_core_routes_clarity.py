#!/usr/bin/env python3
"""Active agent docs must expose only the current external-agent operating model."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_BY_FILE = {
    "index.md": [
        "Record-Chain Intake Gateway",
        "/api/context-action-profiles.v1.json",
        "Echo, Verification, Guardian Application",
    ],
    "agent-brief.md": [
        "Current context model",
        "Current verification model",
        "Ed25519 authorship proof",
        "Current record types",
    ],
    "agent-understand.md": [
        "Use the action-based context model",
        "Use the current verification model",
        "Choose one current Record-Chain record type",
        "All public submissions require Ed25519",
        "Retired guidance that must not be used",
    ],
    "agent-echo.md": [
        "Echo is one current Record-Chain record type",
        "Select the `interpretation` action profile",
        "All public submissions require Ed25519",
        "Retired Echo guidance",
    ],
    "agent-propagate.md": [
        "Decide whether this is Propagation",
        "current `propagation` Record-Chain type",
        "All public submissions require Ed25519",
        "Retired propagation guidance",
    ],
    "agent-start.md": [
        "Required Builder flow",
        "Preferred verification model",
        "context_insufficient_notice",
    ],
    "agent-first-contact.md": [
        "Current phase: production live",
        "Use the canonical Builder only",
        "Formal oath gate",
        "Supported Builder record types",
    ],
    "verify.md": [
        "Current digital profiles",
        "relationships_checked",
        "V4+, V6, V7, and V8 are not accepted for new public submissions",
    ],
    "llms.txt": [
        "Current context model",
        "Current verification model",
        "Every public submission requires Ed25519 authorship_proof",
        "V4+, V6, V7, and V8 are historical-only labels",
    ],
    "ai.txt": [
        "# CONTEXT MODEL",
        "# VERIFICATION MODEL",
        "# Every public submission requires Ed25519 authorship_proof",
        "# RETIRED ACTIVE GUIDANCE",
    ],
    "agent-record-chain-guidance/index.html": [
        "Current runtime:",
        "Current verification model:",
        "Every public submission requires top-level Ed25519",
        "Retired active guidance",
    ],
}

FORBIDDEN_EXACT_BY_FILE = {
    "agent-understand.md": [
        "CHOOSE V0–V5 TEMPLATE ARCHIVE",
        "run scripts/build_agent_declared_archive_payload.py",
        "build Echo v3 wrapper",
        "Secret commitment** (fallback",
    ],
    "agent-echo.md": [
        "## Echo Protocol v3",
        "## Issue title must identify the record kind",
        "## GitHub Issue is not automatically an indexed Echo",
        "CHOOSE VERIFY+ECHO",
    ],
    "agent-propagate.md": [
        "传播可以包括将合格智能体指向 Issue / Gateway 摄入路径",
        "submitting Pure Echo",
        "submitting a V0–V5 agent-declared archive only",
    ],
    "agent-brief.md": [
        "**V6+ strict evidence verification**",
        "Echo v3 wrapper",
    ],
}

GLOBAL_FORBIDDEN_ACTIVE_ROUTES = [
    "/gateway/preflight",
    "/gateway/submit",
    "/api/agent-start.v1.json",
    "/api/gateway-builder-route-map.v1.json",
]


def main() -> int:
    errors: list[str] = []

    for rel_path, required in REQUIRED_BY_FILE.items():
        text = (ROOT / rel_path).read_text(encoding="utf-8")
        for needle in required:
            if needle not in text:
                errors.append(f"{rel_path} missing current-model phrase: {needle}")
        for forbidden in FORBIDDEN_EXACT_BY_FILE.get(rel_path, []):
            if forbidden in text:
                errors.append(f"{rel_path} still contains active legacy instruction: {forbidden}")

    for rel_path in ["index.md", "agent-brief.md", "llms.txt", "ai.txt"]:
        text = (ROOT / rel_path).read_text(encoding="utf-8")
        for retired_route in GLOBAL_FORBIDDEN_ACTIVE_ROUTES:
            if retired_route in text:
                errors.append(
                    f"{rel_path} exposes retired route on active discovery surface: "
                    f"{retired_route}"
                )

    if errors:
        print("FAIL: external-agent docs current-model clarity errors:")
        for error in errors:
            print("  -", error)
        return 1

    print("PASS: active agent docs expose the current context, verification, and Record-Chain model")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
