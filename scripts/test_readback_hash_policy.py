#!/usr/bin/env python3
"""Verify current Record-Chain oath/readback fields and reject retired Gateway fields."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT_FIELDS = {
    "participant_readback_sha256",
    "canonical_oath_text_sha256",
    "oath_policy_sha256",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> int:
    schema_text = (ROOT / "api/record-chain-submission-schema.v1.json").read_text(encoding="utf-8")
    builder_text = (ROOT / "downloads/record-chain-builder.mjs").read_text(encoding="utf-8")
    first_contact = json.loads((ROOT / "api/agent-first-contact.json").read_text(encoding="utf-8"))

    for field in sorted(CURRENT_FIELDS):
        require(field in schema_text, f"submission schema missing {field}")
        require(field in builder_text, f"Builder missing {field}")

    require("agent_readback_sha256" not in schema_text, "current schema contains retired agent_readback_sha256")
    require("agent_readback_sha256" not in builder_text, "current Builder contains retired agent_readback_sha256")
    require(first_contact.get("zero_clone_formal_builder_policy", {}).get("do_not_handwrite_formal_payload") is True,
            "agent-first-contact must forbid handwritten formal payloads")

    for relative in ["index.md", "agent-start.md", "llms.txt", "external-agent-quickstart.md"]:
        text = (ROOT / relative).read_text(encoding="utf-8").lower()
        require("handwrite" in text and ("submission" in text or "payload" in text),
                f"{relative} must warn against handwritten submissions")
        require("agent_readback_sha256" not in text, f"{relative} contains retired agent_readback_sha256")

    print("READBACK_HASH_POLICY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
