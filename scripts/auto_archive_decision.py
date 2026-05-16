#!/usr/bin/env python3
"""Auto Archive Decision — converts archive readiness into GitHub labels, comments, and close-state.

Usage:
    python3 scripts/auto_archive_decision.py \
        --archive-readiness archive-readiness.json \
        --json
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


COMMENT_TEMPLATE_READY = """\
<!-- trinity-auto-archive-decision:v1 sha256={decision_sha256} -->

### Automated Archive Decision

Result: `{action}`

Archive kind: `{requested_archive_kind}`

Archive ready: `{archive_ready}`

This automated decision is based on:
- Claim Gate output
- Archive Readiness Gate
- Artifact bundle references
- Boundary acknowledgements

This record remains:
- not authority
- not amendment
- not independent attestation
- not successor reception
"""

COMMENT_TEMPLATE_BLOCKED = """\
### Archive Blocked

Archive kind requested: `{requested_archive_kind}`

Archive ready: `false`

Blocking reasons:
{blocking_reasons_md}

Required next actions:
{required_next_actions_md}

No archive labels were applied.
"""


def compute_decision_sha256(readiness):
    """Compute SHA-256 of the readiness output for comment anchoring."""
    canonical = json.dumps(readiness, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def build_decision(readiness):
    """Build auto archive decision from readiness output."""
    action = readiness.get("auto_archive_action", "none")
    archive_ready = readiness.get("archive_ready", False)
    auto_archive_allowed = readiness.get("auto_archive_allowed", False)
    record_intent = readiness.get("record_intent", "intake_only")
    requested_kind = readiness.get("requested_archive_kind", "none")
    blocking_reasons = readiness.get("blocking_reasons", [])
    required_next = readiness.get("required_next_actions", [])

    # --- Determine issue creation, labels, close behavior ---
    should_create_issue = True
    should_close_issue = False
    close_reason = None
    labels_to_add = []
    labels_to_remove = []
    comment_markdown = None

    if archive_ready and auto_archive_allowed:
        # Auto archive path
        labels_to_add = list(readiness.get("auto_labels", []))
        should_close_issue = readiness.get("auto_close_issue", False)
        close_reason = readiness.get("close_reason")

        # Labels to remove on success
        labels_to_remove = [
            "archive:not-ready",
            "archive:blocked",
            "needs-artifacts",
            "needs-provenance-proof",
            "needs-level-downgrade"
        ]

        decision_sha = compute_decision_sha256(readiness)
        comment_markdown = COMMENT_TEMPLATE_READY.format(
            decision_sha256=decision_sha,
            action=action,
            requested_archive_kind=requested_kind,
            archive_ready=str(archive_ready).lower()
        )

    elif not archive_ready and record_intent == "auto_archive_candidate":
        # Blocked archive — do not create issue
        should_create_issue = False
        action = action if action in ("block", "needs_more_evidence") else "block"

        br_md = "\n".join(f"- [{br['code']}] {br['message']}" for br in blocking_reasons) if blocking_reasons else "- (none)"
        next_md = "\n".join(f"- {a}" for a in required_next) if required_next else "- (none)"
        comment_markdown = COMMENT_TEMPLATE_BLOCKED.format(
            requested_archive_kind=requested_kind,
            blocking_reasons_md=br_md,
            required_next_actions_md=next_md
        )

    elif not archive_ready and record_intent == "intake_only":
        # Intake only — no archive labels
        action = "none"
        should_create_issue = True  # Normal intake proceeds

    # Successor reception: always block, never create issue
    if requested_kind == "successor_reception_candidate":
        action = "block"
        should_create_issue = False
        labels_to_add = []
        labels_to_remove = []

    # --- Forbidden outputs ---
    # Do not output manual-review flags
    # Do not output successor-reception or independent-attestation labels
    forbidden_labels = {"successor-reception", "independent-attestation"}
    labels_to_add = [l for l in labels_to_add if l not in forbidden_labels]

    return {
        "schema": "trinityaccord.auto-archive-decision.v1",
        "action": action,
        "should_create_issue": should_create_issue,
        "should_close_issue": should_close_issue,
        "close_reason": close_reason,
        "labels_to_add": labels_to_add,
        "labels_to_remove": labels_to_remove,
        "comment_markdown": comment_markdown
    }


def main():
    parser = argparse.ArgumentParser(description="Auto Archive Decision")
    parser.add_argument("--archive-readiness", required=True, help="Path to archive readiness JSON")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    readiness = load_json(args.archive_readiness)
    decision = build_decision(readiness)

    if args.json:
        print(json.dumps(decision, indent=2, ensure_ascii=False))
    else:
        print(f"action: {decision['action']}")
        print(f"should_create_issue: {decision['should_create_issue']}")
        print(f"should_close_issue: {decision['should_close_issue']}")
        if decision["labels_to_add"]:
            print(f"labels_to_add: {', '.join(decision['labels_to_add'])}")


if __name__ == "__main__":
    main()
