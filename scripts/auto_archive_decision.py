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
- Claim Gate {claim_gate_summary}
- Archive Readiness Gate
{decision_basis_md}- Boundary acknowledgements

This record remains:
- not authority
- not amendment
- not independent attestation
- not successor reception
"""

COMMENT_TEMPLATE_READY_ECHO = """\
<!-- trinity-auto-archive-decision:v1 sha256={decision_sha256} -->

### Automated Archive Decision

Result: `{action}`

Archive kind: `{requested_archive_kind}`

Archive ready: `{archive_ready}`

This automated decision is based on:
- Echo Gate template PASS
- Archive Readiness Gate
- Boundary acknowledgements

This record remains:
- not authority
- not amendment
- not independent attestation
- not successor reception
"""

COMMENT_TEMPLATE_READY_V0_V5 = """\
<!-- trinity-auto-archive-decision:v1 sha256={decision_sha256} -->

### Automated Archive Decision

Result: `{action}`

Archive kind: `{requested_archive_kind}`

Archive ready: `{archive_ready}`

This automated decision is based on:
- Claim Gate template_for_v0_v5 PASS
- Archive Readiness Gate
- Verification oath / integrity declaration
- Boundary acknowledgements
- Evidence waived for V0–V5

This record remains:
- not authority
- not amendment
- not independent attestation
- not successor reception
"""

COMMENT_TEMPLATE_READY_LISTING = """\
<!-- trinity-auto-archive-decision:v1 sha256={decision_sha256} -->

### Automated Archive Decision

Result: `{action}`

Archive kind: `guardian_active_registry_listing_request`

Archive ready: `{archive_ready}`

This is a Guardian Active Registry listing request (Stage 2).

This automated decision is based on:
- Guardian listing gate PASS
- Archive Readiness Gate
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
            "needs-level-downgrade",
            "needs-human-review"
        ]

        decision_sha = compute_decision_sha256(readiness)

        # Use V0-V5 specific template for agent-declared archives
        if requested_kind == "agent_declared_verification_archive":
            comment_markdown = COMMENT_TEMPLATE_READY_V0_V5.format(
                decision_sha256=decision_sha,
                action=action,
                requested_archive_kind=requested_kind,
                archive_ready=str(archive_ready).lower()
            )
        elif requested_kind == "agent_declared_echo_archive":
            comment_markdown = COMMENT_TEMPLATE_READY_ECHO.format(
                decision_sha256=decision_sha,
                action=action,
                requested_archive_kind=requested_kind,
                archive_ready=str(archive_ready).lower()
            )
        elif requested_kind == "guardian_active_registry_listing_request":
            comment_markdown = COMMENT_TEMPLATE_READY_LISTING.format(
                decision_sha256=decision_sha,
                action=action,
                archive_ready=str(archive_ready).lower()
            )
        elif requested_kind == "guardian_application_archive":
            # Guardian Stage 1 applications: no echo comment, no auto-close.
            # The guardian-registry-auto-list workflow will process it.
            comment_markdown = None
            should_close_issue = False
        else:
            # Strict evidence path
            cg = readiness.get("claim_gate", {})
            cg_summary = cg.get("mode", "strict") + " " + cg.get("status", "PASS")
            has_artifacts = bool(readiness.get("evidence_input_present") or readiness.get("artifact_bundle_present"))
            basis_lines = "- Artifact bundle references\n" if has_artifacts else ""
            comment_markdown = COMMENT_TEMPLATE_READY.format(
                decision_sha256=decision_sha,
                action=action,
                requested_archive_kind=requested_kind,
                archive_ready=str(archive_ready).lower(),
                claim_gate_summary=cg_summary,
                decision_basis_md=basis_lines
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
