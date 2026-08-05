#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ACTION_MINIMUMS = {
    "echo": "CC-3",
    "verification": "CC-3",
    "guardian_application": "CC-3",
    "guardian_retirement": "CC-1",
    "propagation": "CC-2",
    "correction": "CC-1",
    "classification_update": "CC-2",
}


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path: str, value: dict) -> None:
    (ROOT / path).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


readiness = load("api/context-readiness-levels.json")
crl5 = next(item for item in readiness["levels"] if item["id"] == "CRL-5")
crl5["min_context_depth"] = "CC-1"
crl5["context_minimum_is_action_dependent"] = True
crl5["minimum_context_by_action"] = ACTION_MINIMUMS
crl5["note"] = (
    "CRL-5 is an action-ready state, not one universal context threshold. "
    "CC-1 is the lowest floor among supported formal actions; the exact minimum is derived from the selected record type. "
    "Public Echo, public Verification, and Guardian Application require CC-3."
)
save("api/context-readiness-levels.json", readiness)

mapping = load("api/crl-to-context-depth-mapping.json")
crl5_map = next(item for item in mapping["mappings"] if item["crl"] == "CRL-5")
crl5_map["min_context_depth"] = "CC-1"
crl5_map["context_minimum_is_action_dependent"] = True
crl5_map["minimum_context_by_action"] = ACTION_MINIMUMS
crl5_map["note"] = (
    "CRL-5 is action-ready. CC-1 is the lowest floor among supported formal actions; "
    "the exact public minimum is selected from minimum_context_by_action and is recomputed by Builder and Gateway."
)
mapping["legacy_verification_level_action_minimums_boundary"] = {
    "status": "historical_compatibility_and_private_check_only",
    "not_current_public_submission_rule": True,
    "current_public_verification_minimum": "CC-3",
    "current_public_replacement": "action_minimum_requirements.public_verification_submission",
    "rule": (
        "The V0-V2 CC-2 entries below may describe archived records or a narrow private technical check that is not publicly submitted. "
        "Every new public Verification record requires CC-3 plus actual task sources and fresh operations."
    ),
}
save("api/crl-to-context-depth-mapping.json", mapping)

print("CRL-5 action-dependent minimums clarified.")
